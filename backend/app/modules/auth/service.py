"""Auth biznes-mantiqi: login, token berish/rotatsiya, brute-force himoya."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.modules.auth.models import LoginAttempt, RefreshToken
from app.modules.auth.schemas import RegisterRequest, TokenPair
from app.modules.users.models import User, UserRole
from app.modules.users.schemas import UserCreate
from app.modules.users.service import UserService
from app.shared.exceptions import AuthError, RateLimitError


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserService(db)

    # --- Ro'yxatdan o'tish ---
    async def register(self, data: RegisterRequest) -> User:
        """Ochiq ro'yxatdan o'tish — har doim CITIZEN roli bilan."""
        return await self.users.create(
            UserCreate(
                email=data.email,
                full_name=data.full_name,
                phone=data.phone,
                password=data.password,
                role=UserRole.CITIZEN,
            )
        )

    # --- Brute-force himoya ---
    async def _check_brute_force(self, email: str) -> None:
        window_start = datetime.now(UTC) - timedelta(minutes=settings.login_lockout_minutes)
        failed = await self.db.scalar(
            select(func.count())
            .select_from(LoginAttempt)
            .where(
                LoginAttempt.email == email.lower(),
                LoginAttempt.successful.is_(False),
                LoginAttempt.created_at >= window_start,
            )
        )
        if (failed or 0) >= settings.login_max_attempts:
            raise RateLimitError(
                f"Juda ko'p muvaffaqiyatsiz urinish. "
                f"{settings.login_lockout_minutes} daqiqadan so'ng qayta urinib ko'ring"
            )

    async def _record_attempt(self, email: str, ip: str | None, ok: bool) -> None:
        # MUHIM: darhol commit qilamiz. Aks holda muvaffaqiyatsiz login
        # AuthError ko'targanda so'rov tranzaksiyasi rollback bo'lib, urinish
        # yozuvi ham yo'qoladi va brute-force himoya ishlamaydi.
        self.db.add(LoginAttempt(email=email.lower(), ip_address=ip, successful=ok))
        await self.db.commit()

    # --- Login ---
    async def login(
        self, email: str, password: str, ip: str | None = None
    ) -> tuple[User, TokenPair]:
        await self._check_brute_force(email)
        user = await self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            await self._record_attempt(email, ip, ok=False)
            raise AuthError("Email yoki parol noto'g'ri")
        if not user.is_active:
            raise AuthError("Foydalanuvchi bloklangan")
        await self._record_attempt(email, ip, ok=True)
        tokens = await self._issue_tokens(user)
        return user, tokens

    # --- Token berish ---
    async def _issue_tokens(self, user: User) -> TokenPair:
        access, _, _ = create_access_token(str(user.id), extra={"role": user.role.value})
        refresh, jti, expires_at = create_refresh_token(str(user.id))
        self.db.add(RefreshToken(jti=jti, user_id=user.id, expires_at=expires_at))
        await self.db.flush()
        return TokenPair(access_token=access, refresh_token=refresh)

    # --- Refresh (rotation) ---
    async def refresh(self, refresh_token: str) -> TokenPair:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise AuthError("Refresh token yaroqsiz")

        jti = payload.get("jti")
        result = await self.db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
        stored = result.scalar_one_or_none()

        if stored is None or stored.revoked:
            raise AuthError("Refresh token bekor qilingan yoki topilmadi")
        # SQLite tz-aware datetime saqlamaydi; naive bo'lsa UTC deb qabul qilamiz.
        expires_at = stored.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at < datetime.now(UTC):
            raise AuthError("Refresh token muddati o'tgan")

        # Rotatsiya: eski token'ni bekor qilamiz, yangisini beramiz
        stored.revoked = True
        await self.db.flush()

        user = await self.db.get(User, int(payload["sub"]))
        if user is None or not user.is_active:
            raise AuthError("Foydalanuvchi topilmadi yoki faol emas")
        return await self._issue_tokens(user)

    # --- Logout (barcha refresh token'larni bekor qilish) ---
    async def logout(self, user_id: int) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
            .values(revoked=True)
        )
        await self.db.flush()
