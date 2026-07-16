"""Boshlang'ich ma'lumot: super-admin yaratadi (idempotent).

Ishlatish:  python -m app.scripts.seed
"""

import asyncio

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.modules.users.service import UserService


async def main() -> None:
    async with AsyncSessionLocal() as db:
        service = UserService(db)
        user = await service.ensure_superadmin(
            email=settings.first_superadmin_email,
            password=settings.first_superadmin_password,
            full_name="Super Admin",
        )
        await db.commit()
        print(f"✅ Super-admin tayyor: {user.email} (id={user.id}, role={user.role.value})")


if __name__ == "__main__":
    asyncio.run(main())
