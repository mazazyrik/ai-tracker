from typing import Any, Dict, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.core.config import Settings
from app.services.user_service import get_or_create_user


class UserMiddleware(BaseMiddleware):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        from_user = data.get('event_from_user')
        if from_user is not None:
            user = await get_or_create_user(from_user.id, self.settings)
            data['user'] = user
        return await handler(event, data)


