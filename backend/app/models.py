"""Barcha ORM modellarini bitta joyda import qiladi.

Alembic va `Base.metadata` barcha jadvallarni ko'rishi uchun kerak.
Yangi modul qo'shilganda uning modelini shu yerga qo'shing.
"""

from app.modules.auth.models import LoginAttempt, RefreshToken
from app.modules.emergency.models import CallEvent, EmergencyCall
from app.modules.users.models import User
from app.shared.base import Base

__all__ = [
    "Base",
    "User",
    "RefreshToken",
    "LoginAttempt",
    "EmergencyCall",
    "CallEvent",
]
