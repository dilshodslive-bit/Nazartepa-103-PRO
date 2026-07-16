"""Foydalanuvchilar biznes-mantiqi."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.modules.users.models import User, UserRole
from app.modules.users.schemas import UserCreate, UserUpdate
from app.shared.exceptions import ConflictError, NotFoundError


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, user_id: int) -> User:
        user = await self.db.get(User, user_id)
        if user is None:
            raise NotFoundError("Foydalanuvchi topilmadi")
        return user

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    async def list(self, offset: int, limit: int) -> tuple[list[User], int]:
        total = await self.db.scalar(select(func.count()).select_from(User)) or 0
        result = await self.db.execute(
            select(User).order_by(User.id.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total

    async def create(self, data: UserCreate) -> User:
        if await self.get_by_email(data.email):
            raise ConflictError("Bu email allaqachon ro'yxatdan o'tgan")
        user = User(
            email=data.email.lower(),
            full_name=data.full_name,
            phone=data.phone,
            hashed_password=hash_password(data.password),
            role=data.role,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: int, data: UserUpdate) -> User:
        user = await self.get(user_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def ensure_superadmin(self, email: str, password: str, full_name: str) -> User:
        """Seed uchun: super-admin bo'lmasa yaratadi (idempotent)."""
        existing = await self.get_by_email(email)
        if existing:
            return existing
        user = User(
            email=email.lower(),
            full_name=full_name,
            hashed_password=hash_password(password),
            role=UserRole.SUPER_ADMIN,
            is_active=True,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
