from app.core.settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, UserRole
from app.core.security import hash_password

async def seed_admin(db: AsyncSession) -> None:
    username = settings.ADMIN_USERNAME
    email = settings.ADMIN_EMAIL
    password = settings.ADMIN_PASSWORD

    result = await db.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none():
        return

    admin = User(
        username=username,
        email=email,
        passwordHash=hash_password(password),
        role=UserRole.admin,
        isActive=True,
    )

    db.add(admin)
    await db.commit()