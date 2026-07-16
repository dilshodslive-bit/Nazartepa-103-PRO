"""Foydalanuvchilar HTTP endpoint'lari."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.auth.rbac import require_role
from app.modules.users.models import User, UserRole
from app.modules.users.schemas import UserCreate, UserRead, UserUpdate
from app.modules.users.service import UserService
from app.shared.pagination import Page, PageParams

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def read_me(current: User = Depends(get_current_user)) -> User:
    """Joriy foydalanuvchi profili."""
    return current


@router.get("", response_model=Page[UserRead])
async def list_users(
    params: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
) -> Page[UserRead]:
    """Foydalanuvchilar ro'yxati (admin+)."""
    items, total = await UserService(db).list(params.offset, params.size)
    return Page(
        items=[UserRead.model_validate(u) for u in items],
        total=total,
        page=params.page,
        size=params.size,
    )


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
) -> User:
    """Yangi foydalanuvchi yaratish (admin+ istalgan rol bilan)."""
    return await UserService(db).create(data)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
) -> User:
    """Foydalanuvchini yangilash (admin+)."""
    return await UserService(db).update(user_id, data)
