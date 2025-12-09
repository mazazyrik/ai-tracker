from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from app.bot.handlers.menu.menu import menu_router
from app.bot.handlers.tasks.tasks import tasks_router
from app.bot.handlers.timers.timers import timers_router
from app.bot.handlers.stats.stats import stats_router
from app.bot.handlers.ai.ai import ai_router
from app.bot.middlewares.user_middleware import UserMiddleware
from app.core.config import Settings
from app.core.redis import create_redis


def create_bot(settings: Settings) -> Bot:
    return Bot(
        token=settings.bot.token,
        default=DefaultBotProperties(parse_mode='HTML'),
    )


def create_dispatcher(settings: Settings) -> Dispatcher:
    redis = create_redis(settings)
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)
    dp['settings'] = settings
    dp['redis'] = redis
    dp.update.outer_middleware(UserMiddleware(settings=settings))
    dp.include_router(menu_router)
    dp.include_router(tasks_router)
    dp.include_router(timers_router)
    dp.include_router(stats_router)
    dp.include_router(ai_router)
    return dp



