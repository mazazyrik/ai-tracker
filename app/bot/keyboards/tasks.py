from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.callbacks.menu import MenuActionCallback
from app.bot.callbacks.stats import StatsActionCallback
from app.bot.callbacks.tasks import TaskActionCallback, TimerActionCallback
from app.db.models.task import Task, TaskStatus
from app.services.timers_service import format_seconds


def tasks_list_keyboard(tasks: List[Task]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for task in tasks:
        if task.status == TaskStatus.COMPLETED:
            action = TimerActionCallback(action='extend', task_id=task.id).pack()
            text = f'✅ {task.title} — {format_seconds(task.planned_seconds)}'
        else:
            action = TimerActionCallback(action='start', task_id=task.id).pack()
            text = f'{task.title} — {format_seconds(task.planned_seconds)} [▶️]'
        rows.append([InlineKeyboardButton(text=text, callback_data=action)])
    add_task = TaskActionCallback(action='add', task_id=0).pack()
    stats = StatsActionCallback(action='open').pack()
    back_menu = MenuActionCallback(action='main').pack()
    rows.append([InlineKeyboardButton(
        text='➕ Добавить задачу', callback_data=add_task)])
    rows.append([InlineKeyboardButton(
        text='📊 Статистика', callback_data=stats)])
    rows.append([InlineKeyboardButton(
        text='⬅️ В меню', callback_data=back_menu)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def timer_controls_keyboard(task_id: int) -> InlineKeyboardMarkup:
    pause = TimerActionCallback(action='pause', task_id=task_id).pack()
    complete = TimerActionCallback(action='complete', task_id=task_id).pack()
    add_time = TimerActionCallback(action='add_5', task_id=task_id).pack()
    back_list = TimerActionCallback(
        action='back_to_list', task_id=task_id).pack()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='⏸ Пауза', callback_data=pause),
                InlineKeyboardButton(text='✔️ Завершить',
                                     callback_data=complete),
            ],
            [InlineKeyboardButton(text='➕ +5 мин', callback_data=add_time)],
            [InlineKeyboardButton(text='⬅️ К задачам',
                                  callback_data=back_list)],
        ],
    )


def timer_paused_keyboard(task_id: int) -> InlineKeyboardMarkup:
    resume = TimerActionCallback(action='resume', task_id=task_id).pack()
    back_list = TimerActionCallback(
        action='back_to_list', task_id=task_id).pack()
    back_menu = MenuActionCallback(action='main').pack()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='▶️ Продолжить',
                                  callback_data=resume)],
            [InlineKeyboardButton(text='⬅️ К задачам',
                                  callback_data=back_list)],
            [InlineKeyboardButton(text='⬅️ В меню', callback_data=back_menu)],
        ],
    )


def timer_finished_keyboard(task_id: int) -> InlineKeyboardMarkup:
    back_list = TimerActionCallback(
        action='back_to_list', task_id=task_id).pack()
    back_menu = MenuActionCallback(action='main').pack()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='⬅️ К задачам',
                                  callback_data=back_list)],
            [InlineKeyboardButton(text='⬅️ В меню', callback_data=back_menu)],
        ],
    )


def timer_extend_keyboard(task_id: int) -> InlineKeyboardMarkup:
    extend_add = TimerActionCallback(
        action='extend_add', task_id=task_id).pack()
    back_list = TimerActionCallback(
        action='back_to_list', task_id=task_id).pack()
    back_menu = MenuActionCallback(action='main').pack()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='➕ Добавить времени',
                                  callback_data=extend_add)],
            [InlineKeyboardButton(text='⬅️ К задачам',
                                  callback_data=back_list)],
            [InlineKeyboardButton(text='⬅️ В меню', callback_data=back_menu)],
        ],
    )
