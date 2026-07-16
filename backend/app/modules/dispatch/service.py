"""Dispatch biznes-mantiqi: eng yaqin bo'sh brigadani topib tayinlash."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ambulance.models import Ambulance, AmbulanceStatus
from app.modules.dispatch.models import Dispatch, DispatchStatus
from app.modules.emergency.models import CallStatus, EmergencyCall
from app.modules.emergency.service import EmergencyCallService
from app.modules.realtime.manager import manager
from app.shared.exceptions import AppError, NotFoundError
from app.shared.geo import eta_minutes, haversine_km


class DispatchError(AppError):
    status_code = 409
    detail = "Tayinlab bo'lmadi"


class DispatchService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _available_with_location(self) -> list[Ambulance]:
        result = await self.db.execute(
            select(Ambulance).where(
                Ambulance.status == AmbulanceStatus.AVAILABLE,
                Ambulance.latitude.is_not(None),
                Ambulance.longitude.is_not(None),
            )
        )
        return list(result.scalars().all())

    def _nearest(
        self, call: EmergencyCall, ambulances: list[Ambulance]
    ) -> tuple[Ambulance, float]:
        """Eng yaqin brigadani tanlaydi. Iloji bo'lsa AI tavsiya qilgan ixtisosga
        mos brigadalar orasidan, aks holda umumiy eng yaqinini."""
        preferred = [
            a for a in ambulances if a.brigade_type == call.ai_recommended_brigade
        ]
        pool = preferred or ambulances
        best = min(
            pool,
            key=lambda a: haversine_km(
                call.latitude, call.longitude, a.latitude, a.longitude
            ),
        )
        dist = haversine_km(call.latitude, call.longitude, best.latitude, best.longitude)
        return best, dist

    async def dispatch_call(
        self, call_id: int, assigned_by_id: int | None, ambulance_id: int | None = None
    ) -> Dispatch:
        call = await self.db.get(EmergencyCall, call_id)
        if call is None:
            raise NotFoundError("Murojaat topilmadi")
        if call.latitude is None or call.longitude is None:
            raise DispatchError("Murojaatda koordinata yo'q — tayinlab bo'lmaydi")
        if call.status != CallStatus.TRIAGED:
            raise DispatchError(
                "Faqat 'triaged' holatidagi murojaatni tayinlash mumkin"
            )

        if ambulance_id is not None:
            amb = await self.db.get(Ambulance, ambulance_id)
            if amb is None:
                raise NotFoundError("Ambulans topilmadi")
            if amb.status != AmbulanceStatus.AVAILABLE:
                raise DispatchError("Tanlangan brigada bo'sh emas")
            if amb.latitude is None or amb.longitude is None:
                raise DispatchError("Brigadaning joylashuvi noma'lum")
            distance = haversine_km(
                call.latitude, call.longitude, amb.latitude, amb.longitude
            )
        else:
            available = await self._available_with_location()
            if not available:
                raise DispatchError("Bo'sh brigada topilmadi")
            amb, distance = self._nearest(call, available)

        eta = eta_minutes(distance)
        dispatch = Dispatch(
            call_id=call.id,
            ambulance_id=amb.id,
            assigned_by_id=assigned_by_id,
            distance_km=round(distance, 2),
            eta_minutes=eta,
            status=DispatchStatus.ACTIVE,
        )
        self.db.add(dispatch)

        # Brigadani band qilamiz
        amb.status = AmbulanceStatus.DISPATCHED
        amb.current_call_id = call.id

        # Murojaat holatini triaged -> dispatched (audit hodisasi bilan)
        await EmergencyCallService(self.db).change_status(
            call.id,
            CallStatus.DISPATCHED,
            actor_id=assigned_by_id,
            note=f"{amb.callsign} tayinlandi (~{eta} daqiqa, {round(distance, 1)} km)",
        )

        await self.db.flush()
        await self.db.refresh(dispatch)

        await manager.broadcast(
            {
                "type": "dispatch",
                "call_id": call.id,
                "ambulance_id": amb.id,
                "callsign": amb.callsign,
                "distance_km": dispatch.distance_km,
                "eta_minutes": eta,
            }
        )
        return dispatch

    async def get_for_call(self, call_id: int) -> Dispatch | None:
        """Murojaatning eng oxirgi tayinlanishi."""
        result = await self.db.execute(
            select(Dispatch)
            .where(Dispatch.call_id == call_id)
            .order_by(Dispatch.id.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
