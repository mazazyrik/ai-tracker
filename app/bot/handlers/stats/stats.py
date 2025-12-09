from datetime import date, timedelta

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.bot.callbacks.stats import StatsActionCallback
from app.bot.keyboards.stats import stats_menu_keyboard
from app.core.logger import get_logger
from app.db.models.user import User
from app.services.stats_service import get_daily_stats, get_weekly_stats


logger = get_logger('stats_handlers')

stats_router = Router()


@stats_router.message(F.text == '📊 Статистика')
async def open_stats_menu(message: Message, user: User) -> None:
    logger.info('open_stats_menu user_id=%s', user.id)
    await message.answer('Статистика', reply_markup=stats_menu_keyboard())


@stats_router.callback_query(StatsActionCallback.filter(F.action == 'open'))
async def open_stats_menu_cb(callback: CallbackQuery, user: User) -> None:
    logger.info('open_stats_menu_cb user_id=%s', user.id)
    await callback.message.edit_text('Статистика', reply_markup=stats_menu_keyboard())
    await callback.answer()


@stats_router.callback_query(StatsActionCallback.filter(F.action == 'daily'))
async def show_daily_stats(callback: CallbackQuery, user: User) -> None:
    today = date.today()
    stats = await get_daily_stats(user, today)
    logger.info('show_daily_stats user_id=%s tasks=%s', user.id, len(stats.tasks))
    text = (
        f'📅 Сегодня: {today.isoformat()}\n'
        f'Задач: {len(stats.tasks)}\n'
        f'План: {stats.planned_seconds // 60} мин\n'
        f'Факт: {stats.spent_seconds // 60} мин'
    )
    await callback.message.edit_text(text, reply_markup=stats_menu_keyboard())
    await callback.answer()


@stats_router.callback_query(StatsActionCallback.filter(F.action == 'weekly'))
async def show_weekly_stats(callback: CallbackQuery, user: User) -> None:
    today = date.today()
    start = today - timedelta(days=today.weekday())
    weekly = await get_weekly_stats(user, start)
    logger.info('show_weekly_stats user_id=%s', user.id)
    lines = [f'📈 Неделя {weekly.start.isoformat()} - {weekly.end.isoformat()}']
    for day, stats in weekly.by_day.items():
        lines.append(
            f'{day.isoformat()}: задач {len(stats.tasks)}, план {stats.planned_seconds // 60} мин, факт {stats.spent_seconds // 60} мин',
        )
    await callback.message.edit_text('\n'.join(lines), reply_markup=stats_menu_keyboard())
    await callback.answer()
