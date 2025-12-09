from datetime import date, timedelta

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.bot.callbacks.ai import AiActionCallback
from app.bot.keyboards.ai import ai_menu_keyboard
from app.core.config import Settings
from app.core.logger import get_logger
from app.db.models.user import User
from app.services.ai_service import generate_daily_summary, generate_weekly_report


logger = get_logger('ai_handlers')

ai_router = Router()


@ai_router.callback_query(AiActionCallback.filter())
async def ai_menu(callback: CallbackQuery, callback_data: AiActionCallback, user: User, settings: Settings) -> None:
    if callback_data.action == 'daily':
        logger.info('ai_daily user_id=%s', user.id)
        text = await generate_daily_summary(user.id, date.today(), settings)
        if not text:
            text = 'Пока не получилось собрать саммари.'
    elif callback_data.action == 'weekly':
        logger.info('ai_weekly user_id=%s', user.id)
        today = date.today()
        start = today - timedelta(days=today.weekday())
        text = await generate_weekly_report(user.id, start, settings)
        if not text:
            text = 'Пока не получилось собрать отчёт.'
    else:
        text = 'Неизвестное действие.'
    await callback.message.edit_text(text, reply_markup=ai_menu_keyboard())
    await callback.answer()
