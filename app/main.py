import asyncio

from aiogram import Dispatcher

from app.bot.bot import create_bot, create_dispatcher
from app.core.config import Settings, get_settings
from app.core.logger import get_logger
from app.db.init import close_db, init_db


logger = get_logger('main')


async def _run_bot(settings: Settings) -> None:
    await init_db(settings, with_schema=True)
    bot = create_bot(settings)
    dp: Dispatcher = create_dispatcher(settings)
    try:
        await dp.start_polling(bot)
    finally:
        await close_db()
        await bot.session.close()


def main() -> None:
    settings = get_settings()
    try:
        asyncio.run(_run_bot(settings))
    except KeyboardInterrupt:
        logger.info('bot stopped')


if __name__ == '__main__':
    main()


