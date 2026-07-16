"""Tez yordam murojaatlari biznes-mantiqi."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai_triage.provider import TriageResult
from app.modules.ai_triage.service import TriageService
from app.modules.emergency.models import (
    CallEvent,
    CallStatus,
    EmergencyCall,
    Priority,
    PrioritySource,
)
from app.modules.emergency.schemas import EmergencyCallCreate, EmergencyCallUpdate
from app.shared.exceptions import AppError, NotFoundError

# Ruxsat etilgan holat o'tishlari. Yakuniy holatlar (completed, cancelled) — bo'sh.
ALLOWED_TRANSITIONS: dict[CallStatus, set[CallStatus]] = {
    CallStatus.NEW: {CallStatus.TRIAGED, CallStatus.CANCELLED},
    CallStatus.TRIAGED: {CallStatus.DISPATCHED, CallStatus.CANCELLED},
    CallStatus.DISPATCHED: {CallStatus.EN_ROUTE, CallStatus.CANCELLED},
    CallStatus.EN_ROUTE: {CallStatus.ON_SCENE, CallStatus.CANCELLED},
    CallStatus.ON_SCENE: {CallStatus.COMPLETED, CallStatus.CANCELLED},
    CallStatus.COMPLETED: set(),
    CallStatus.CANCELLED: set(),
}


class InvalidStatusTransition(AppError):
    status_code = 409
    detail = "Holatni bunday o'zgartirib bo'lmaydi"


class EmergencyCallService:
    def __init__(self, db: AsyncSession, triage: TriageService | None = None) -> None:
        self.db = db
        self.triage = triage or TriageService()

    async def get(self, call_id: int) -> EmergencyCall:
        call = await self.db.get(EmergencyCall, call_id)
        if call is None:
            raise NotFoundError("Murojaat topilmadi")
        return call

    async def list(
        self,
        offset: int,
        limit: int,
        status: CallStatus | None = None,
        priority: Priority | None = None,
    ) -> tuple[list[EmergencyCall], int]:
        conditions = []
        if status is not None:
            conditions.append(EmergencyCall.status == status)
        if priority is not None:
            conditions.append(EmergencyCall.priority == priority)

        count_stmt = select(func.count()).select_from(EmergencyCall)
        list_stmt = select(EmergencyCall).order_by(EmergencyCall.id.desc())
        for cond in conditions:
            count_stmt = count_stmt.where(cond)
            list_stmt = list_stmt.where(cond)

        total = await self.db.scalar(count_stmt) or 0
        result = await self.db.execute(list_stmt.offset(offset).limit(limit))
        return list(result.scalars().all()), total

    async def create(
        self, data: EmergencyCallCreate, created_by_id: int | None
    ) -> EmergencyCall:
        call = EmergencyCall(
            caller_phone=data.caller_phone,
            caller_name=data.caller_name,
            address_text=data.address_text,
            latitude=data.latitude,
            longitude=data.longitude,
            complaint=data.complaint,
            media_urls=data.media_urls,
            status=CallStatus.NEW,
            created_by_id=created_by_id,
        )
        self.db.add(call)
        await self.db.flush()
        # Boshlang'ich audit hodisasi
        self.db.add(
            CallEvent(
                call_id=call.id,
                actor_id=created_by_id,
                from_status=None,
                to_status=CallStatus.NEW,
                note="Murojaat yaratildi",
            )
        )
        # Avtomatik AI triaj (rule_based default — offline; xatoda zaxira ishlaydi)
        result = await self.triage.assess(call.complaint)
        self._apply_triage(call, result)
        await self.db.flush()
        await self.db.refresh(call)
        return call

    def _apply_triage(self, call: EmergencyCall, result: TriageResult) -> None:
        """AI triaj natijasini murojaatga yozadi (faqat qo'lda o'zgartirilmagan bo'lsa)."""
        # Operator qo'lda belgilagan ustuvorlikni AI ustiga yozib yubormaydi
        if call.priority_source != PrioritySource.MANUAL:
            call.priority = result.priority
            call.priority_source = PrioritySource.AI
        call.ai_severity = result.severity
        call.ai_recommended_brigade = result.recommended_brigade
        call.ai_confidence = result.confidence
        call.ai_reason = result.reason
        call.ai_provider = result.provider

    async def run_triage(self, call_id: int) -> EmergencyCall:
        """Murojaatni qayta baholaydi (operator qo'lda so'raganda)."""
        call = await self.get(call_id)
        result = await self.triage.assess(call.complaint)
        self._apply_triage(call, result)
        await self.db.flush()
        await self.db.refresh(call)
        return call

    async def update(self, call_id: int, data: EmergencyCallUpdate) -> EmergencyCall:
        call = await self.get(call_id)
        fields = data.model_dump(exclude_unset=True)
        for field, value in fields.items():
            setattr(call, field, value)
        # Ustuvorlik qo'lda o'zgartirilsa — manba "manual" bo'lib qoladi
        if "priority" in fields:
            call.priority_source = PrioritySource.MANUAL
        await self.db.flush()
        await self.db.refresh(call)
        return call

    async def change_status(
        self,
        call_id: int,
        new_status: CallStatus,
        actor_id: int | None,
        note: str | None = None,
    ) -> EmergencyCall:
        call = await self.get(call_id)
        old_status = call.status

        if new_status == old_status:
            raise InvalidStatusTransition("Murojaat allaqachon shu holatda")
        if new_status not in ALLOWED_TRANSITIONS[old_status]:
            raise InvalidStatusTransition(
                f"'{old_status.value}' → '{new_status.value}' o'tishi mumkin emas"
            )

        call.status = new_status
        self.db.add(
            CallEvent(
                call_id=call.id,
                actor_id=actor_id,
                from_status=old_status,
                to_status=new_status,
                note=note,
            )
        )
        await self.db.flush()
        await self.db.refresh(call)
        return call

    async def list_events(self, call_id: int) -> list[CallEvent]:
        await self.get(call_id)  # mavjudligini tekshiradi (404)
        result = await self.db.execute(
            select(CallEvent)
            .where(CallEvent.call_id == call_id)
            .order_by(CallEvent.id)
        )
        return list(result.scalars().all())
