"""Emergency Call Pydantic sxemalari (I/O)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.emergency.models import CallStatus, Priority, PrioritySource


class EmergencyCallCreate(BaseModel):
    caller_phone: str = Field(min_length=3, max_length=32)
    caller_name: str | None = Field(default=None, max_length=255)
    address_text: str | None = Field(default=None, max_length=512)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    complaint: str = Field(min_length=3, max_length=5000)
    media_urls: list[str] = Field(default_factory=list, max_length=20)


class EmergencyCallUpdate(BaseModel):
    """Murojaat tafsilotlarini tahrirlash (holatdan tashqari)."""

    caller_phone: str | None = Field(default=None, min_length=3, max_length=32)
    caller_name: str | None = Field(default=None, max_length=255)
    address_text: str | None = Field(default=None, max_length=512)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    complaint: str | None = Field(default=None, min_length=3, max_length=5000)
    media_urls: list[str] | None = Field(default=None, max_length=20)
    priority: Priority | None = None


class StatusUpdate(BaseModel):
    """Holatni o'zgartirish so'rovi."""

    status: CallStatus
    note: str | None = Field(default=None, max_length=512)


class CallEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_id: int | None
    from_status: CallStatus | None
    to_status: CallStatus
    note: str | None
    created_at: datetime


class EmergencyCallRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    caller_phone: str
    caller_name: str | None
    address_text: str | None
    latitude: float | None
    longitude: float | None
    complaint: str
    media_urls: list[str]
    status: CallStatus
    priority: Priority | None
    priority_source: PrioritySource | None
    # AI triaj natijasi
    ai_severity: int | None
    ai_recommended_brigade: str | None
    ai_confidence: float | None
    ai_reason: str | None
    ai_provider: str | None
    created_by_id: int | None
    created_at: datetime
    updated_at: datetime
