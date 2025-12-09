from datetime import date

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from redis.asyncio import Redis

from app.bot.callbacks.tasks import TimerActionCallback
from app.bot.keyboards.tasks import (
    timer_controls_keyboard,
    timer_extend_keyboard,
    timer_finished_keyboard,
    timer_paused_keyboard,
    tasks_list_keyboard,
)
from app.bot.states.tasks import ExtendTaskStates
from app.core.config import Settings
from app.core.logger import get_logger
from app.db.models.task import Task, TaskStatus
from app.db.models.user import User
from app.services.ai_service import generate_all_done_message
from app.services.tasks_service import list_tasks_for_date
from app.services.timers_service import format_seconds, pause_timer, start_timer, stop_timer


logger = get_logger('timers_handlers')

timers_router = Router()


@timers_router.callback_query(TimerActionCallback.filter(F.action == 'start'))
async def timer_start(callback: CallbackQuery, callback_data: TimerActionCallback, user: User, redis: Redis) -> None:
    task = await Task.get_or_none(id=callback_data.task_id, user=user)
    if not task:
        await callback.answer('Задача не найдена.', show_alert=True)
        return
    text = (
        f'⏳ Задача: {task.title}\n'
        f'Прошло: {format_seconds(task.spent_seconds)}\n'
        f'План: {format_seconds(task.planned_seconds)}'
    )
    message = await callback.message.edit_text(text, reply_markup=timer_controls_keyboard(task.id))
    await start_timer(redis, task, chat_id=message.chat.id, message_id=message.message_id)
    logger.info('timer_start user_id=%s task_id=%s', user.id, task.id)
    await callback.answer()


@timers_router.callback_query(TimerActionCallback.filter(F.action == 'pause'))
async def timer_pause(callback: CallbackQuery, callback_data: TimerActionCallback, user: User, redis: Redis) -> None:
    task = await Task.get_or_none(id=callback_data.task_id, user=user)
    if not task:
        await callback.answer('Задача не найдена.', show_alert=True)
        return
    total = await pause_timer(redis, task)
    text = (
        f'⏸ Пауза\n'
        f'Задача: {task.title}\n'
        f'Накоплено: {format_seconds(total)} из {format_seconds(task.planned_seconds)}'
    )
    logger.info('timer_pause user_id=%s task_id=%s total=%s', user.id, task.id, total)
    await callback.message.edit_text(text, reply_markup=timer_paused_keyboard(task.id))
    await callback.answer()


@timers_router.callback_query(TimerActionCallback.filter(F.action == 'resume'))
async def timer_resume(callback: CallbackQuery, callback_data: TimerActionCallback, user: User, redis: Redis) -> None:
    task = await Task.get_or_none(id=callback_data.task_id, user=user)
    if not task:
        await callback.answer('Задача не найдена.', show_alert=True)
        return
    text = (
        f'⏳ Задача: {task.title}\n'
        f'Прошло: {format_seconds(task.spent_seconds)}\n'
        f'План: {format_seconds(task.planned_seconds)}'
    )
    message = await callback.message.edit_text(text, reply_markup=timer_controls_keyboard(task.id))
    await start_timer(redis, task, chat_id=message.chat.id, message_id=message.message_id)
    logger.info('timer_resume user_id=%s task_id=%s', user.id, task.id)
    await callback.answer()


@timers_router.callback_query(TimerActionCallback.filter(F.action == 'complete'))
async def timer_complete(
    callback: CallbackQuery,
    callback_data: TimerActionCallback,
    user: User,
    redis: Redis,
    settings: Settings,
) -> None:
    task = await Task.get_or_none(id=callback_data.task_id, user=user)
    if not task:
        await callback.answer('Задача не найдена.', show_alert=True)
        return
    total = await stop_timer(redis, task, completed=True)
    text = (
        f'⏰ Время вышло!\n'
        f'Задача "{task.title}" завершена.\n'
        f'Факт: {format_seconds(total)} из плана {format_seconds(task.planned_seconds)}.'
    )
    logger.info('timer_complete user_id=%s task_id=%s total=%s', user.id, task.id, total)
    await callback.message.edit_text(text, reply_markup=timer_finished_keyboard(task.id))
    await callback.answer()
    today = date.today()
    tasks_today = await Task.filter(user=user, date=today)
    if tasks_today and all(t.status == TaskStatus.COMPLETED for t in tasks_today):
        extra = await generate_all_done_message(user.id, today, settings)
        if extra:
            await callback.message.answer(extra)


@timers_router.callback_query(TimerActionCallback.filter(F.action == 'add_5'))
async def timer_add_five(callback: CallbackQuery, callback_data: TimerActionCallback, user: User, redis: Redis) -> None:
    task = await Task.get_or_none(id=callback_data.task_id, user=user)
    if not task:
        await callback.answer('Задача не найдена.', show_alert=True)
        return
    await pause_timer(redis, task)
    task.planned_seconds += 5 * 60
    task.status = TaskStatus.ACTIVE
    await task.save()
    text = (
        f'⏳ Задача: {task.title}\n'
        f'Прошло: {format_seconds(task.spent_seconds)}\n'
        f'План: {format_seconds(task.planned_seconds)}'
    )
    message = await callback.message.edit_text(text, reply_markup=timer_controls_keyboard(task.id))
    await start_timer(redis, task, chat_id=message.chat.id, message_id=message.message_id)
    logger.info('timer_add_five user_id=%s task_id=%s', user.id, task.id)
    await callback.answer()


@timers_router.callback_query(TimerActionCallback.filter(F.action == 'back_to_list'))
async def back_to_list(callback: CallbackQuery, user: User) -> None:
    today = date.today()
    tasks = await list_tasks_for_date(user, today)
    if tasks:
        lines = ['📅 Задачи на сегодня:']
        for idx, t in enumerate(tasks, start=1):
            lines.append(f'{idx}. {t.title} — {t.planned_seconds // 60} мин')
        await callback.message.edit_text('\n'.join(lines), reply_markup=tasks_list_keyboard(tasks))
    else:
        await callback.message.edit_text('📅 Задач на сегодня нет.')
    await callback.answer()


@timers_router.callback_query(TimerActionCallback.filter(F.action == 'extend'))
async def extend_task(callback: CallbackQuery, callback_data: TimerActionCallback, user: User, state: FSMContext) -> None:
    task = await Task.get_or_none(id=callback_data.task_id, user=user)
    if not task:
        await callback.answer('Задача не найдена.', show_alert=True)
        return
    text = (
        f'✅ Задача "{task.title}" выполнена.\n'
        f'Факт: {format_seconds(task.spent_seconds)}.\n'
        f'Что дальше?'
    )
    await state.clear()
    await callback.message.edit_text(text, reply_markup=timer_extend_keyboard(task.id))
    await callback.answer()


@timers_router.callback_query(TimerActionCallback.filter(F.action == 'extend_add'))
async def extend_task_start(callback: CallbackQuery, callback_data: TimerActionCallback, user: User, state: FSMContext) -> None:
    task = await Task.get_or_none(id=callback_data.task_id, user=user)
    if not task:
        await callback.answer('Задача не найдена.', show_alert=True)
        return
    await state.set_state(ExtendTaskStates.minutes)
    await state.update_data(task_id=task.id)
    await callback.message.edit_text('Сколько минут ещё добавить? (1–999)')
    await callback.answer()


@timers_router.message(ExtendTaskStates.minutes)
async def extend_task_minutes(message: Message, state: FSMContext, user: User, redis: Redis) -> None:
    text = (message.text or '').strip()
    if not text.isdigit():
        await message.answer('Нужно ввести число от 1 до 999.')
        return
    minutes = int(text)
    if minutes <= 0 or minutes > 999:
        await message.answer('Нужно ввести число от 1 до 999.')
        return
    data = await state.get_data()
    task_id = int(data.get('task_id') or 0)
    task = await Task.get_or_none(id=task_id, user=user)
    if not task:
        await message.answer('Задача не найдена, начни заново.')
        await state.clear()
        return
    task.planned_seconds += minutes * 60
    task.status = TaskStatus.ACTIVE
    await task.save()
    await state.clear()
    text_out = (
        f'⏳ Задача: {task.title}\n'
        f'Прошло: {format_seconds(task.spent_seconds)}\n'
        f'Новый план: {format_seconds(task.planned_seconds)}'
    )
    out = await message.answer(text_out, reply_markup=timer_controls_keyboard(task.id))
    await start_timer(redis, task, chat_id=out.chat.id, message_id=out.message_id)
    logger.info(
        'task_extended user_id=%s task_id=%s minutes=%s',
        user.id,
        task.id,
        minutes,
    )
