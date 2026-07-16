"""Dispatch Pydantic sxemalari."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.dispatch.models import DispatchStatus


class DispatchCreate(BaseModel):
    """Tayinlash so'rovi. ambulance_id berilmasa — eng yaqin bo'sh brigada tanlanadi."""

    ambulance_id: int | None = Field(default=None, ge=1)


class DispatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    call_id: int
    ambulance_id: int
    assigned_by_id: int | None
    distance_km: float
    eta_minutes: int
    status: DispatchStatus
    created_at: datetime
