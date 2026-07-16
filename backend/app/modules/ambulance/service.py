"""Ambulans biznes-mantiqi (GPS/holat yangilanishi realtime'ga uzatiladi)."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ambulance.models import Ambulance, AmbulanceStatus
from app.modules.ambulance.schemas import AmbulanceCreate, AmbulanceUpdate
from app.modules.realtime.manager import manager
from app.shared.exceptions import ConflictError, NotFoundError


class AmbulanceService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, ambulance_id: int) -> Ambulance:
        amb = await self.db.get(Ambulance, ambulance_id)
        if amb is None:
            raise NotFoundError("Ambulans topilmadi")
        return amb

    async def get_by_callsign(self, callsign: str) -> Ambulance | None:
        result = await self.db.execute(
            select(Ambulance).where(Ambulance.callsign == callsign)
        )
        return result.scalar_one_or_none()

    async def list(
        self, offset: int, limit: int, status: AmbulanceStatus | None = None
    ) -> tuple[list[Ambulance], int]:
        count_stmt = select(func.count()).select_from(Ambulance)
        list_stmt = select(Ambulance).order_by(Ambulance.id)
        if status is not None:
            count_stmt = count_stmt.where(Ambulance.status == status)
            list_stmt = list_stmt.where(Ambulance.status == status)
        total = await self.db.scalar(count_stmt) or 0
        result = await self.db.execute(list_stmt.offset(offset).limit(limit))
        return list(result.scalars().all()), total

    async def create(self, data: AmbulanceCreate) -> Ambulance:
        if await self.get_by_callsign(data.callsign):
            raise ConflictError("Bu chaqiruv belgisi (callsign) allaqachon mavjud")
        amb = Ambulance(
            callsign=data.callsign,
            plate=data.plate,
            brigade_type=data.brigade_type,
            latitude=data.latitude,
            longitude=data.longitude,
            last_location_at=datetime.now(UTC)
            if data.latitude is not None
            else None,
        )
        self.db.add(amb)
        await self.db.flush()
        await self.db.refresh(amb)
        return amb

    async def update(self, ambulance_id: int, data: AmbulanceUpdate) -> Ambulance:
        amb = await self.get(ambulance_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(amb, field, value)
        await self.db.flush()
        await self.db.refresh(amb)
        return amb

    async def update_location(
        self, ambulance_id: int, latitude: float, longitude: float
    ) -> Ambulance:
        amb = await self.get(ambulance_id)
        amb.latitude = latitude
        amb.longitude = longitude
        amb.last_location_at = datetime.now(UTC)
        await self.db.flush()
        await self.db.refresh(amb)
        await manager.broadcast(
            {
                "type": "ambulance_location",
                "ambulance_id": amb.id,
                "callsign": amb.callsign,
                "latitude": latitude,
                "longitude": longitude,
                "status": amb.status.value,
            }
        )
        return amb

    async def change_status(
        self, ambulance_id: int, status: AmbulanceStatus
    ) -> Ambulance:
        amb = await self.get(ambulance_id)
        amb.status = status
        # Bo'shab qolsa — joriy murojaatdan uziladi
        if status in (AmbulanceStatus.AVAILABLE, AmbulanceStatus.OFFLINE):
            amb.current_call_id = None
        await self.db.flush()
        await self.db.refresh(amb)
        await manager.broadcast(
            {
                "type": "ambulance_status",
                "ambulance_id": amb.id,
                "callsign": amb.callsign,
                "status": amb.status.value,
            }
        )
        return amb
