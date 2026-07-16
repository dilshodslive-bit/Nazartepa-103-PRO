"""SQLAlchemy Base va umumiy mixinlar."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Barcha modellar uchun asosiy klass."""


class IntPKMixin:
    """Butun sonli birlamchi kalit."""

    id: Mapped[int] = mapped_column(primary_key=True, index=True)


class TimestampMixin:
    """created_at / updated_at maydonlari (server tomonida boshqariladi)."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
