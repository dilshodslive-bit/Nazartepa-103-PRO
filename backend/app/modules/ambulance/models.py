"""Tez yordam brigadasi (ambulans) modeli."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base import Base, IntPKMixin, TimestampMixin


class AmbulanceStatus(enum.StrEnum):
    """Brigada holati."""

    AVAILABLE = "available"  # bo'sh, tayinlashga tayyor
    DISPATCHED = "dispatched"  # tayinlandi, hali yo'lga chiqmagan
    EN_ROUTE = "en_route"  # voqea joyiga ketyapti
    ON_SCENE = "on_scene"  # voqea joyida
    BUSY = "busy"  # band (bemorni tashiyapti va h.k.)
    OFFLINE = "offline"  # xizmatda emas


class Ambulance(IntPKMixin, TimestampMixin, Base):
    __tablename__ = "ambulances"

    callsign: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    plate: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # Brigada ixtisosi — ai_recommended_brigade qiymatlari bilan mos
    brigade_type: Mapped[str] = mapped_column(String(64), default="umumiy", nullable=False)

    status: Mapped[AmbulanceStatus] = mapped_column(
        Enum(
            AmbulanceStatus,
            name="ambulance_status",
            native_enum=False,
            length=32,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=AmbulanceStatus.AVAILABLE,
        nullable=False,
        index=True,
    )

    # --- Joriy GPS koordinatalari ---
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_location_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Joriy tayinlangan murojaat (bo'sh bo'lsa null)
    current_call_id: Mapped[int | None] = mapped_column(
        ForeignKey("emergency_calls.id", ondelete="SET NULL"), index=True, nullable=True
    )
