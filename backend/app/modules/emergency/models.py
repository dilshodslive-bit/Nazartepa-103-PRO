"""Tez yordam murojaati (EmergencyCall) va uning audit hodisalari."""

import enum
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base import Base, IntPKMixin, TimestampMixin


class CallStatus(enum.StrEnum):
    """Murojaat hayotiy sikli.

    Oqim: new → triaged → dispatched → en_route → on_scene → completed.
    Istalgan yakunlanmagan holatdan `cancelled` ga o'tish mumkin.
    """

    NEW = "new"
    TRIAGED = "triaged"
    DISPATCHED = "dispatched"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Priority(enum.StrEnum):
    """Triaj ustuvorligi (M3'da AI to'ldiradi)."""

    RED = "red"  # hayotiy xavf — zudlik bilan
    YELLOW = "yellow"  # shoshilinch, lekin barqaror
    GREEN = "green"  # shoshilinch emas


class PrioritySource(enum.StrEnum):
    """Ustuvorlikni kim belgiladi."""

    AI = "ai"  # avtomatik triaj
    MANUAL = "manual"  # operator qo'lda o'zgartirdi


def _enum_col(enum_cls: type[enum.StrEnum], name: str) -> Enum:
    """Enum nomini emas, qiymatini saqlaydigan portativ ustun (users.role bilan bir xil uslub)."""
    return Enum(
        enum_cls,
        name=name,
        native_enum=False,
        length=32,
        values_callable=lambda e: [m.value for m in e],
    )


class EmergencyCall(IntPKMixin, TimestampMixin, Base):
    __tablename__ = "emergency_calls"

    # --- Murojaatchi va joylashuv ---
    caller_phone: Mapped[str] = mapped_column(String(32), nullable=False)
    caller_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_text: Mapped[str | None] = mapped_column(String(512), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Shikoyat ---
    complaint: Mapped[str] = mapped_column(Text, nullable=False)
    media_urls: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    # --- Holat va ustuvorlik ---
    status: Mapped[CallStatus] = mapped_column(
        _enum_col(CallStatus, "call_status"),
        default=CallStatus.NEW,
        nullable=False,
        index=True,
    )
    priority: Mapped[Priority | None] = mapped_column(
        _enum_col(Priority, "call_priority"),
        default=None,
        nullable=True,
        index=True,
    )
    priority_source: Mapped[PrioritySource | None] = mapped_column(
        _enum_col(PrioritySource, "priority_source"), default=None, nullable=True
    )

    # --- AI triaj natijasi (M3) ---
    ai_severity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ai_recommended_brigade: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ai_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ai_provider: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # --- Kim qabul qildi (operator yoki murojaatchi) ---
    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )

    events: Mapped[list["CallEvent"]] = relationship(
        back_populates="call",
        cascade="all, delete-orphan",
        order_by="CallEvent.id",
        lazy="selectin",
    )


class CallEvent(IntPKMixin, Base):
    """Audit yozuvi: murojaat holati kim tomonidan qanday o'zgartirildi."""

    __tablename__ = "call_events"

    call_id: Mapped[int] = mapped_column(
        ForeignKey("emergency_calls.id", ondelete="CASCADE"), index=True, nullable=False
    )
    actor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    from_status: Mapped[CallStatus | None] = mapped_column(
        _enum_col(CallStatus, "event_from_status"), nullable=True
    )
    to_status: Mapped[CallStatus] = mapped_column(
        _enum_col(CallStatus, "event_to_status"), nullable=False
    )
    note: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True, nullable=False
    )

    call: Mapped["EmergencyCall"] = relationship(back_populates="events")
