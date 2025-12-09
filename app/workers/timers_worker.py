import asyncio
from datetime import date, datetime, timezone

from aiogram import Bot
from redis.asyncio import Redis

from app.bot.keyboards.tasks import timer_controls_keyboard, timer_finished_keyboard
from app.core.config import Settings, get_settings
from app.core.constants import REDIS_ACTIVE_TIMER_PREFIX
from app.core.logger import get_logger
from app.core.redis import create_redis
from app.db.init import init_db, close_db
from app.db.models.task import Task, TaskStatus
from app.db.models.user import User
from app.services.ai_service import generate_all_done_message
from app.services.timers_service import _key, format_seconds, get_active_timer, stop_timer


logger = get_logger('timers_worker')


async def _process_timers(bot: Bot, redis: Redis, settings: Settings) -> None:
    keys = await redis.keys(f'{REDIS_ACTIVE_TIMER_PREFIX}*')
    if not keys:
        return
    for key in keys:
        raw = await redis.hgetall(key)
        if not raw:
            continue
        task_id_str = key.split(':')[-1]
        try:
            task_id = int(task_id_str)
        except ValueError:
            continue
        data = await get_active_timer(redis, task_id)
        if not data:
            continue
        now = datetime.now(timezone.utc)
        delta = int((now - data.started_at).total_seconds())
        if delta < 0:
            continue
        total = data.accumulated_seconds + delta
        update_mapping = {
            'accumulated_seconds': total,
            'started_at': now.isoformat(),
            'last_update_at': now.isoformat(),
        }
        await redis.hset(_key(task_id), mapping=update_mapping)
        task = await Task.get_or_none(id=task_id)
        if not task:
            continue
        if data.chat_id is not None and data.message_id is not None:
            if not data.last_update_at or (now - data.last_update_at).total_seconds() >= 1:
                text = (
                    f'⏳ Задача: {task.title}\n'
                    f'Прошло: {format_seconds(total)}\n'
                    f'План: {format_seconds(task.planned_seconds)}'
                )
                try:
                    await bot.edit_message_text(
                        chat_id=data.chat_id,
                        message_id=data.message_id,
                        text=text,
                        reply_markup=timer_controls_keyboard(task.id),
                    )
                except Exception as exc:
                    logger.error(
                        'edit_message_text error task_id=%s: %s', task.id, exc)
        if total >= task.planned_seconds:
            await stop_timer(redis, task, completed=True)
            user = await User.get(id=task.user_id)
            chat_id = user.telegram_id
            text = (
                f'⏰ Время вышло!\n'
                f'Задача "{task.title}" завершена.\n'
                f'Факт: {format_seconds(total)} из плана {format_seconds(task.planned_seconds)}.'
            )
            await bot.send_message(chat_id, text, reply_markup=timer_finished_keyboard(task.id))
            today = date.today()
            tasks_today = await Task.filter(user_id=user.id, date=today)
            if tasks_today and all(t.status == TaskStatus.COMPLETED for t in tasks_today):
                extra = await generate_all_done_message(user.id, today, settings)
                if extra:
                    await bot.send_message(chat_id, extra)


async def main() -> None:
    settings: Settings = get_settings()
    await init_db(settings, with_schema=False)
    redis = create_redis(settings)
    bot = Bot(token=settings.bot.token)
    try:
        while True:
            try:
                await _process_timers(bot, redis, settings)
            except Exception as exc:
                logger.error('timers loop error: %s', exc)
            await asyncio.sleep(1)
    finally:
        await close_db()
        await redis.close()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
