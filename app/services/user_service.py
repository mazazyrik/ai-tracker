from typing import Optional

from app.core.config import Settings
from app.db.models.user import User


async def get_or_create_user(telegram_id: int, settings: Settings) -> User:
    """Get user by telegram id or create new."""
    user = await User.get_or_none(telegram_id=telegram_id)
    if user:
        return user
    timezone = settings.timezone
    return await User.create(telegram_id=telegram_id, timezone=timezone)


async def update_timezone(user: User, timezone: str) -> User:
    """Update user timezone."""
    user.timezone = timezone
    await user.save()
    return user


async def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by internal id."""
    return await User.get_or_none(id=user_id)
