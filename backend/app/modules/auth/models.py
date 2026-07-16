"""Auth modellari: refresh token'lar va login urinishlari."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base import Base, IntPKMixin, TimestampMixin


class RefreshToken(IntPKMixin, TimestampMixin, Base):
    """Saqlangan refresh token (rotation + revocation uchun).

    Token'ning o'zi emas, uning `jti` (JWT ID) saqlanadi. Rotatsiya:
    yangi token berilganda eskisi `revoked=True` bo'ladi.
    """

    __tablename__ = "refresh_tokens"

    jti: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")  # noqa: F821


class LoginAttempt(IntPKMixin, Base):
    """Brute-force himoya uchun login urinishlari tarixi."""

    __tablename__ = "login_attempts"

    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    successful: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True, nullable=False
    )
