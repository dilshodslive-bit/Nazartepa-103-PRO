"""Dispatch (tayinlash) modeli — murojaatga brigada biriktirish tarixi."""

import enum

from sqlalchemy import Enum, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base import Base, IntPKMixin, TimestampMixin


class DispatchStatus(enum.StrEnum):
    ACTIVE = "active"  # tayinlangan, jarayonda
    COMPLETED = "completed"  # yakunlandi
    CANCELLED = "cancelled"  # bekor qilindi


class Dispatch(IntPKMixin, TimestampMixin, Base):
    __tablename__ = "dispatches"

    call_id: Mapped[int] = mapped_column(
        ForeignKey("emergency_calls.id", ondelete="CASCADE"), index=True, nullable=False
    )
    ambulance_id: Mapped[int] = mapped_column(
        ForeignKey("ambulances.id", ondelete="CASCADE"), index=True, nullable=False
    )
    assigned_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    eta_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[DispatchStatus] = mapped_column(
        Enum(
            DispatchStatus,
            name="dispatch_status",
            native_enum=False,
            length=32,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=DispatchStatus.ACTIVE,
        nullable=False,
        index=True,
    )
