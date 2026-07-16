"""Dispatch HTTP endpoint'lari (murojaatga brigada tayinlash)."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.rbac import require_role
from app.modules.dispatch.schemas import DispatchCreate, DispatchRead
from app.modules.dispatch.service import DispatchService
from app.modules.users.models import User, UserRole
from app.shared.exceptions import NotFoundError

router = APIRouter(prefix="/calls", tags=["dispatch"])


@router.post(
    "/{call_id}/dispatch",
    response_model=DispatchRead,
    status_code=status.HTTP_201_CREATED,
)
async def dispatch_call(
    call_id: int,
    data: DispatchCreate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_role(UserRole.DISPATCHER)),
) -> DispatchRead:
    """Murojaatga brigada tayinlash (dispatcher+).

    `ambulance_id` berilmasa — eng yaqin bo'sh brigada (iloji bo'lsa AI tavsiya
    qilgan ixtisosga mos) avtomatik tanlanadi."""
    dispatch = await DispatchService(db).dispatch_call(
        call_id, assigned_by_id=current.id, ambulance_id=data.ambulance_id
    )
    return DispatchRead.model_validate(dispatch)


@router.get("/{call_id}/dispatch", response_model=DispatchRead)
async def get_dispatch(
    call_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.OPERATOR)),
) -> DispatchRead:
    """Murojaatga tayinlangan brigada ma'lumoti (operator+)."""
    dispatch = await DispatchService(db).get_for_call(call_id)
    if dispatch is None:
        raise NotFoundError("Bu murojaatga brigada tayinlanmagan")
    return DispatchRead.model_validate(dispatch)
