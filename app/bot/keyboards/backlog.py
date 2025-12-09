from datetime import date
from typing import Dict, List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.callbacks.backlog import BacklogActionCallback, BacklogDayCallback
from app.bot.callbacks.menu import MenuActionCallback
from app.db.models.task import Task
from app.services.timers_service import format_seconds


def backlog_menu_keyboard() -> InlineKeyboardMarkup:
    open_days = BacklogActionCallback(action='days').pack()
    add_future = BacklogActionCallback(action='add_future').pack()
    back_menu = MenuActionCallback(action='main').pack()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='📅 Дни беклога', callback_data=open_days)],
            [InlineKeyboardButton(text='➕ Задача на дату', callback_data=add_future)],
            [InlineKeyboardButton(text='⬅️ В меню', callback_data=back_menu)],
        ],
    )


def backlog_days_keyboard(by_day: Dict[date, List[Task]]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for day, tasks in sorted(by_day.items()):
        total = sum(t.planned_seconds for t in tasks)
        text = f'{day.isoformat()} — {len(tasks)} задач, план {format_seconds(total)}'
        cb = BacklogDayCallback(day=day.isoformat()).pack()
        rows.append([InlineKeyboardButton(text=text, callback_data=cb)])
    back = BacklogActionCallback(action='back').pack()
    rows.append([InlineKeyboardButton(text='⬅️ Назад', callback_data=back)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def backlog_tasks_keyboard(day: date) -> InlineKeyboardMarkup:
    back_days = BacklogActionCallback(action='days').pack()
    back_menu = MenuActionCallback(action='main').pack()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f'⬅️ Дни ({day.isoformat()})', callback_data=back_days)],
            [InlineKeyboardButton(text='⬅️ В меню', callback_data=back_menu)],
        ],
    )


