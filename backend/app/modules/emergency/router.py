"""Tez yordam murojaatlari HTTP endpoint'lari."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.auth.rbac import require_role
from app.modules.emergency.models import CallStatus, Priority
from app.modules.emergency.schemas import (
    CallEventRead,
    EmergencyCallCreate,
    EmergencyCallRead,
    EmergencyCallUpdate,
    StatusUpdate,
)
from app.modules.emergency.service import EmergencyCallService
from app.modules.users.models import User, UserRole
from app.shared.pagination import Page, PageParams

router = APIRouter(prefix="/calls", tags=["emergency"])


@router.post("", response_model=EmergencyCallRead, status_code=status.HTTP_201_CREATED)
async def create_call(
    data: EmergencyCallCreate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> EmergencyCallRead:
    """Yangi murojaat qabul qilish (istalgan autentifikatsiyalangan foydalanuvchi)."""
    call = await EmergencyCallService(db).create(data, created_by_id=current.id)
    return EmergencyCallRead.model_validate(call)


@router.get("", response_model=Page[EmergencyCallRead])
async def list_calls(
    params: PageParams = Depends(),
    status_filter: CallStatus | None = Query(default=None, alias="status"),
    priority: Priority | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.OPERATOR)),
) -> Page[EmergencyCallRead]:
    """Murojaatlar ro'yxati (operator+), holat/ustuvorlik bo'yicha filtr."""
    items, total = await EmergencyCallService(db).list(
        params.offset, params.size, status=status_filter, priority=priority
    )
    return Page(
        items=[EmergencyCallRead.model_validate(c) for c in items],
        total=total,
        page=params.page,
        size=params.size,
    )


@router.get("/{call_id}", response_model=EmergencyCallRead)
async def get_call(
    call_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.OPERATOR)),
) -> EmergencyCallRead:
    """Bitta murojaat tafsilotlari (operator+)."""
    call = await EmergencyCallService(db).get(call_id)
    return EmergencyCallRead.model_validate(call)


@router.patch("/{call_id}", response_model=EmergencyCallRead)
async def update_call(
    call_id: int,
    data: EmergencyCallUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.OPERATOR)),
) -> EmergencyCallRead:
    """Murojaat tafsilotlarini tahrirlash (operator+)."""
    call = await EmergencyCallService(db).update(call_id, data)
    return EmergencyCallRead.model_validate(call)


@router.patch("/{call_id}/status", response_model=EmergencyCallRead)
async def change_call_status(
    call_id: int,
    data: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_role(UserRole.OPERATOR)),
) -> EmergencyCallRead:
    """Murojaat holatini o'zgartirish — oqim qoidalari tekshiriladi (operator+)."""
    call = await EmergencyCallService(db).change_status(
        call_id, data.status, actor_id=current.id, note=data.note
    )
    return EmergencyCallRead.model_validate(call)


@router.post("/{call_id}/triage", response_model=EmergencyCallRead)
async def retriage_call(
    call_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_role(UserRole.OPERATOR)),
) -> EmergencyCallRead:
    """Murojaatni AI orqali qayta baholash (operator+). Qo'lda o'zgartirilgan
    ustuvorlik saqlanadi, faqat AI tavsiyalari yangilanadi."""
    call = await EmergencyCallService(db).run_triage(call_id)
    return EmergencyCallRead.model_validate(call)


@router.get("/{call_id}/events", response_model=list[CallEventRead])
async def list_call_events(
    call_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.OPERATOR)),
) -> list[CallEventRead]:
    """Murojaat audit tarixi — kim qachon holatni o'zgartirdi (operator+)."""
    events = await EmergencyCallService(db).list_events(call_id)
    return [CallEventRead.model_validate(e) for e in events]
