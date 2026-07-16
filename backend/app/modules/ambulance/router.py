"""Ambulans HTTP endpoint'lari."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.ambulance.models import AmbulanceStatus
from app.modules.ambulance.schemas import (
    AmbulanceCreate,
    AmbulanceRead,
    AmbulanceUpdate,
    LocationUpdate,
    StatusUpdate,
)
from app.modules.ambulance.service import AmbulanceService
from app.modules.auth.rbac import require_role
from app.modules.users.models import User, UserRole
from app.shared.pagination import Page, PageParams

router = APIRouter(prefix="/ambulances", tags=["ambulance"])


@router.post("", response_model=AmbulanceRead, status_code=status.HTTP_201_CREATED)
async def create_ambulance(
    data: AmbulanceCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
) -> AmbulanceRead:
    """Yangi brigada qo'shish (admin+)."""
    amb = await AmbulanceService(db).create(data)
    return AmbulanceRead.model_validate(amb)


@router.get("", response_model=Page[AmbulanceRead])
async def list_ambulances(
    params: PageParams = Depends(),
    status_filter: AmbulanceStatus | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.OPERATOR)),
) -> Page[AmbulanceRead]:
    """Brigadalar ro'yxati (operator+), holat bo'yicha filtr."""
    items, total = await AmbulanceService(db).list(
        params.offset, params.size, status=status_filter
    )
    return Page(
        items=[AmbulanceRead.model_validate(a) for a in items],
        total=total,
        page=params.page,
        size=params.size,
    )


@router.get("/{ambulance_id}", response_model=AmbulanceRead)
async def get_ambulance(
    ambulance_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.OPERATOR)),
) -> AmbulanceRead:
    """Bitta brigada (operator+)."""
    amb = await AmbulanceService(db).get(ambulance_id)
    return AmbulanceRead.model_validate(amb)


@router.patch("/{ambulance_id}", response_model=AmbulanceRead)
async def update_ambulance(
    ambulance_id: int,
    data: AmbulanceUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
) -> AmbulanceRead:
    """Brigada ma'lumotlarini tahrirlash (admin+)."""
    amb = await AmbulanceService(db).update(ambulance_id, data)
    return AmbulanceRead.model_validate(amb)


@router.patch("/{ambulance_id}/location", response_model=AmbulanceRead)
async def update_location(
    ambulance_id: int,
    data: LocationUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.DISPATCHER)),
) -> AmbulanceRead:
    """Brigada GPS koordinatasini yangilash — jonli xaritaga uzatiladi (dispatcher+)."""
    amb = await AmbulanceService(db).update_location(
        ambulance_id, data.latitude, data.longitude
    )
    return AmbulanceRead.model_validate(amb)


@router.patch("/{ambulance_id}/status", response_model=AmbulanceRead)
async def change_status(
    ambulance_id: int,
    data: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.DISPATCHER)),
) -> AmbulanceRead:
    """Brigada holatini o'zgartirish (dispatcher+)."""
    amb = await AmbulanceService(db).change_status(ambulance_id, data.status)
    return AmbulanceRead.model_validate(amb)
