"""Foydalanuvchi modeli va rollar."""

import enum

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base import Base, IntPKMixin, TimestampMixin


class UserRole(enum.StrEnum):
    """Tizim rollari (RBAC).

    Iyerarxiya (kuchayish tartibida): citizen < operator < dispatcher
    < doctor < admin < super_admin. Iyerarxiya app.modules.auth.rbac da.
    """

    CITIZEN = "citizen"
    OPERATOR = "operator"
    DISPATCHER = "dispatcher"
    DOCTOR = "doctor"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(IntPKMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            native_enum=False,
            length=32,
            # Enum nomi ("CITIZEN") emas, qiymatini ("citizen") saqlaydi
            values_callable=lambda enum: [member.value for member in enum],
        ),
        default=UserRole.CITIZEN,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(  # noqa: F821
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
