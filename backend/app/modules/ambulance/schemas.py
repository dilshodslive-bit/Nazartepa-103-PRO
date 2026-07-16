"""Ambulans Pydantic sxemalari."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.ambulance.models import AmbulanceStatus


class AmbulanceCreate(BaseModel):
    callsign: str = Field(min_length=1, max_length=32)
    plate: str | None = Field(default=None, max_length=32)
    brigade_type: str = Field(default="umumiy", max_length=64)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class AmbulanceUpdate(BaseModel):
    plate: str | None = Field(default=None, max_length=32)
    brigade_type: str | None = Field(default=None, max_length=64)
    status: AmbulanceStatus | None = None


class LocationUpdate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class StatusUpdate(BaseModel):
    status: AmbulanceStatus


class AmbulanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    callsign: str
    plate: str | None
    brigade_type: str
    status: AmbulanceStatus
    latitude: float | None
    longitude: float | None
    last_location_at: datetime | None
    current_call_id: int | None
    created_at: datetime
    updated_at: datetime
