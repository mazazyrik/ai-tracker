from datetime import date, timedelta
from typing import Any, Dict

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.callbacks.backlog import BacklogActionCallback
from app.bot.callbacks.tasks import TaskActionCallback
from app.bot.keyboards.backlog import backlog_menu_keyboard, backlog_days_keyboard, backlog_tasks_keyboard
from app.bot.keyboards.tasks import tasks_list_keyboard
from app.bot.states.tasks import AddFutureTaskStates, AddTaskStates
from app.core.logger import get_logger
from app.db.models.user import User
from app.services.backlog_service import list_backlog, list_backlog_for_day
from app.services.tasks_service import TaskCreateData, create_task, list_tasks_for_date


logger = get_logger('tasks_handlers')

tasks_router = Router()


@tasks_router.callback_query(TaskActionCallback.filter(F.action == 'add'))
async def start_add_task(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    logger.info('start_add_task user_id=%s', user.id)
    await state.set_state(AddTaskStates.title)
    await callback.message.edit_text('Название задачи?')
    await callback.answer()


@tasks_router.message(AddTaskStates.title)
async def add_task_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text or '')
    await state.set_state(AddTaskStates.planned_time)
    await message.answer('Сколько минут планируешь? (например, 25)')


@tasks_router.message(AddTaskStates.planned_time)
async def add_task_planned_time(message: Message, state: FSMContext, user: User) -> None:
    text = (message.text or '').strip()
    if not text.isdigit():
        await message.answer('Нужно ввести число минут.')
        return
    minutes = int(text)
    if minutes <= 0 or minutes > 999:
        await message.answer('Нужно ввести число от 1 до 999.')
        return
    data: Dict[str, Any] = await state.get_data()
    title = str(data.get('title') or '').strip()
    if not title or minutes <= 0:
        await message.answer('Что-то пошло не так, начни добавление задачи заново.')
        await state.clear()
        return
    task_date = date.today()
    await create_task(
        TaskCreateData(
            user=user,
            title=title,
            planned_seconds=minutes * 60,
            task_date=task_date,
        ),
    )
    logger.info('task_created_today user_id=%s title=%s minutes=%s', user.id, title, minutes)
    await state.clear()
    tasks = await list_tasks_for_date(user, task_date)
    header = '📅 Задачи на сегодня:'
    if tasks:
        lines = [header]
        for idx, t in enumerate(tasks, start=1):
            lines.append(f'{idx}. {t.title} — {t.planned_seconds // 60} мин')
        await message.answer('\n'.join(lines), reply_markup=tasks_list_keyboard(tasks))
    else:
        await message.answer(f'{header}\nпока пусто.')


@tasks_router.callback_query(BacklogActionCallback.filter(F.action == 'open'))
async def backlog_open(callback: CallbackQuery, user: User) -> None:
    await callback.message.edit_text('📅 Беклог задач', reply_markup=backlog_menu_keyboard())
    await callback.answer()


@tasks_router.callback_query(BacklogActionCallback.filter(F.action == 'days'))
async def backlog_days(callback: CallbackQuery, user: User) -> None:
    today = date.today()
    by_day = await list_backlog(user, today)
    if not by_day:
        await callback.message.edit_text('На ближайшие дни задач нет.', reply_markup=backlog_menu_keyboard())
    else:
        await callback.message.edit_text('📅 Беклог по дням:', reply_markup=backlog_days_keyboard(by_day))
    await callback.answer()


@tasks_router.callback_query(BacklogActionCallback.filter(F.action == 'back'))
async def backlog_back(callback: CallbackQuery) -> None:
    await callback.message.edit_text('📅 Беклог задач', reply_markup=backlog_menu_keyboard())
    await callback.answer()


@tasks_router.callback_query(BacklogActionCallback.filter(F.action == 'add_future'))
async def start_add_future_task(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    logger.info('start_add_future_task user_id=%s', user.id)
    await state.set_state(AddFutureTaskStates.title)
    await callback.message.edit_text('Название задачи для беклога?')
    await callback.answer()


@tasks_router.message(AddFutureTaskStates.title)
async def add_future_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text or '')
    await state.set_state(AddFutureTaskStates.planned_time)
    await message.answer('Сколько минут планируешь? (например, 25)')


@tasks_router.message(AddFutureTaskStates.planned_time)
async def add_future_time(message: Message, state: FSMContext) -> None:
    text = (message.text or '').strip()
    if not text.isdigit():
        await message.answer('Нужно ввести число минут.')
        return
    minutes = int(text)
    if minutes <= 0 or minutes > 999:
        await message.answer('Нужно ввести число от 1 до 999.')
        return
    await state.update_data(planned_minutes=minutes)
    await state.set_state(AddFutureTaskStates.date)
    await message.answer('На какую дату? Формат ГГГГ-ММ-ДД, не раньше сегодня и не дальше 30 дней.')


@tasks_router.message(AddFutureTaskStates.date)
async def add_future_date(message: Message, state: FSMContext, user: User) -> None:
    text = (message.text or '').strip()
    today = date.today()
    try:
        task_date = date.fromisoformat(text)
    except ValueError:
        await message.answer('Не получилось разобрать дату, нужен формат ГГГГ-ММ-ДД.')
        return
    if task_date < today:
        await message.answer('Дата уже в прошлом, выбери сегодняшнюю или будущую.')
        return
    if task_date > today + timedelta(days=30):
        await message.answer('Слишком далеко. Можно планировать не больше чем на 30 дней вперёд.')
        return
    data: Dict[str, Any] = await state.get_data()
    title = str(data.get('title') or '').strip()
    planned_minutes = int(data.get('planned_minutes') or 0)
    if not title or planned_minutes <= 0:
        await message.answer('Что-то пошло не так, начни добавление задачи заново.')
        await state.clear()
        return
    await create_task(
        TaskCreateData(
            user=user,
            title=title,
            planned_seconds=planned_minutes * 60,
            task_date=task_date,
        ),
    )
    logger.info(
        'task_created_future user_id=%s title=%s minutes=%s date=%s',
        user.id,
        title,
        planned_minutes,
        task_date.isoformat(),
    )
    await state.clear()
    tasks = await list_backlog_for_day(user, task_date)
    if tasks:
        lines = [f'📅 Задачи на {task_date.isoformat()}:']
        for idx, t in enumerate(tasks, start=1):
            lines.append(f'{idx}. {t.title} — {t.planned_seconds // 60} мин')
        await message.answer('\n'.join(lines), reply_markup=backlog_tasks_keyboard(task_date))
    else:
        await message.answer(f'📅 На {task_date.isoformat()} пока пусто.', reply_markup=backlog_tasks_keyboard(task_date))
