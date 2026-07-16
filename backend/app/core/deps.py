"""Umumiy FastAPI dependency'lar (autentifikatsiya)."""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.shared.exceptions import AuthError

# tokenUrl — Swagger UI "Authorize" tugmasi uchun
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_prefix}/auth/login", auto_error=False
)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Access token'dan joriy foydalanuvchini aniqlaydi.

    Sikldan qochish uchun User import shu yerda (lokal).
    """
    from app.modules.users.models import User

    if not token:
        raise AuthError("Token taqdim etilmadi")

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise AuthError("Token yaroqsiz yoki muddati o'tgan")

    user_id = payload.get("sub")
    if user_id is None:
        raise AuthError("Token tarkibi noto'g'ri")

    user = await db.get(User, int(user_id))
    if user is None or not user.is_active:
        raise AuthError("Foydalanuvchi topilmadi yoki faol emas")
    return user
