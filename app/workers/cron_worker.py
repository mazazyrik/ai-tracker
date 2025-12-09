import asyncio
from datetime import date, datetime, time, timedelta, timezone

from aiogram import Bot

from app.core.config import Settings, get_settings
from app.core.logger import get_logger
from app.db.init import close_db, init_db
from app.db.models.user import User
from app.services.ai_service import generate_daily_summary, generate_weekly_report
from app.services.stats_service import get_daily_stats
from app.services.tasks_service import list_active_or_planned_for_today
from app.services.backlog_service import cleanup_old_tasks
from app.bot.keyboards.tasks import tasks_list_keyboard


logger = get_logger('cron_worker')


async def _send_daily_summaries(bot: Bot, settings: Settings) -> None:
    today = date.today()
    users = await User.all()
    for user in users:
        text = await generate_daily_summary(user.id, today, settings)
        if not text:
            continue
        await bot.send_message(user.telegram_id, text)


async def _send_weekly_reports(bot: Bot, settings: Settings) -> None:
    today = date.today()
    start = today - timedelta(days=today.weekday())
    users = await User.all()
    for user in users:
        text = await generate_weekly_report(user.id, start, settings)
        if not text:
            continue
        await bot.send_message(user.telegram_id, text)


async def _send_two_hour_reminders(bot: Bot) -> None:
    today = date.today()
    users = await User.all()
    for user in users:
        stats = await get_daily_stats(user, today)
        remaining = [t for t in stats.tasks if t.status != 'completed']
        if not remaining:
            continue
        lines = ['📅 Осталось на сегодня:']
        for t in remaining:
            lines.append(f'- {t.title}')
        await bot.send_message(user.telegram_id, '\n'.join(lines))


async def _sleep_until(target: datetime) -> None:
    while True:
        now = datetime.now(timezone.utc)
        delta = (target - now).total_seconds()
        if delta <= 0:
            break
        await asyncio.sleep(min(delta, 60))


def _today_utc_at(hour: int, minute: int) -> datetime:
    today = datetime.now(timezone.utc).date()
    return datetime.combine(today, time(hour=hour, minute=minute, tzinfo=timezone.utc))


async def daily_loop(bot: Bot, settings: Settings) -> None:
    while True:
        target = _today_utc_at(settings.cron.daily_hour, settings.cron.daily_minute)
        await _sleep_until(target)
        try:
            await _send_daily_summaries(bot, settings)
        except Exception as exc:
            logger.error('daily summary error: %s', exc)
        await asyncio.sleep(3600)


async def weekly_loop(bot: Bot, settings: Settings) -> None:
    while True:
        now = datetime.now(timezone.utc)
        if now.weekday() == settings.cron.weekly_weekday and now.hour == settings.cron.weekly_hour:
            try:
                await _send_weekly_reports(bot, settings)
            except Exception as exc:
                logger.error('weekly report error: %s', exc)
            await asyncio.sleep(3600)
        await asyncio.sleep(600)


async def reminders_loop(bot: Bot, settings: Settings) -> None:
    while True:
        try:
            await _send_two_hour_reminders(bot)
        except Exception as exc:
            logger.error('reminders error: %s', exc)
        await asyncio.sleep(settings.cron.reminders_interval_hours * 60 * 60)


async def _send_morning_plan(bot: Bot) -> None:
    today = date.today()
    users = await User.all()
    for user in users:
        tasks = await list_active_or_planned_for_today(user, today)
        if not tasks:
            continue
        lines = ['📅 План на сегодня:']
        for idx, t in enumerate(tasks, start=1):
            lines.append(f'{idx}. {t.title} — {t.planned_seconds // 60} мин')
        await bot.send_message(user.telegram_id, '\n'.join(lines), reply_markup=tasks_list_keyboard(tasks))


async def morning_loop(bot: Bot, settings: Settings) -> None:
    while True:
        target = _today_utc_at(settings.cron.morning_hour, settings.cron.morning_minute)
        await _sleep_until(target)
        try:
            await _send_morning_plan(bot)
        except Exception as exc:
            logger.error('morning plan error: %s', exc)
        await asyncio.sleep(3600)


async def _cleanup_loop() -> None:
    while True:
        try:
            today = date.today()
            limit = today - timedelta(days=30)
            await cleanup_old_tasks(limit)
        except Exception as exc:
            logger.error('cleanup error: %s', exc)
        await asyncio.sleep(24 * 60 * 60)


async def main() -> None:
    settings: Settings = get_settings()
    await init_db(settings, with_schema=False)
    bot = Bot(token=settings.bot.token)
    try:
        await asyncio.gather(
            daily_loop(bot, settings),
            weekly_loop(bot, settings),
            reminders_loop(bot, settings),
            morning_loop(bot, settings),
            _cleanup_loop(),
        )
    finally:
        await close_db()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())




