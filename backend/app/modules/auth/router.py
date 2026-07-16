"""Auth HTTP endpoint'lari."""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.auth.schemas import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
)
from app.modules.auth.service import AuthService
from app.modules.users.models import User
from app.modules.users.schemas import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)) -> User:
    """Ochiq ro'yxatdan o'tish (fuqaro/citizen roli)."""
    return await AuthService(db).register(data)


@router.post("/login", response_model=AuthResponse)
async def login(
    data: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """Login — access + refresh token qaytaradi."""
    ip = request.client.host if request.client else None
    user, tokens = await AuthService(db).login(data.email, data.password, ip)
    return AuthResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        user=UserRead.model_validate(user),
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    """Refresh token'ni yangilaydi (rotatsiya: eskisi bekor qilinadi)."""
    return await AuthService(db).refresh(data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> None:
    """Chiqish — foydalanuvchining barcha refresh token'larini bekor qiladi."""
    await AuthService(db).logout(current.id)
