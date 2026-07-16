"""Rol asosidagi kirish nazorati (RBAC).

Rollar iyerarxik: yuqoriroq rol pastroq rolning ruxsatlarini o'z ichiga oladi.
`require_role(min_role)` — foydalanuvchining roli `min_role` darajasidan
past bo'lmasligini talab qiladigan FastAPI dependency.
"""

from collections.abc import Callable

from fastapi import Depends

from app.core.deps import get_current_user
from app.modules.users.models import User, UserRole
from app.shared.exceptions import PermissionError

# Iyerarxiya darajalari (katta son = ko'proq ruxsat)
ROLE_LEVEL: dict[UserRole, int] = {
    UserRole.CITIZEN: 0,
    UserRole.OPERATOR: 1,
    UserRole.DISPATCHER: 2,
    UserRole.DOCTOR: 3,
    UserRole.ADMIN: 4,
    UserRole.SUPER_ADMIN: 5,
}


def require_role(min_role: UserRole) -> Callable[[User], User]:
    """Berilgan darajadan past bo'lmagan rolni talab qiladi."""

    def dependency(current: User = Depends(get_current_user)) -> User:
        if ROLE_LEVEL[current.role] < ROLE_LEVEL[min_role]:
            raise PermissionError(
                f"Ruxsat yo'q: kamida '{min_role.value}' roli talab qilinadi"
            )
        return current

    return dependency


def require_any_role(*roles: UserRole) -> Callable[[User], User]:
    """Ro'yxatdagi rollardan birortasini talab qiladi (aniq mos kelish)."""
    allowed = set(roles)

    def dependency(current: User = Depends(get_current_user)) -> User:
        if current.role not in allowed:
            names = ", ".join(r.value for r in roles)
            raise PermissionError(f"Ruxsat yo'q: {names} rollaridan biri kerak")
        return current

    return dependency
