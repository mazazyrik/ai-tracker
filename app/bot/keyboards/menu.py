from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.callbacks.backlog import BacklogActionCallback
from app.bot.callbacks.stats import StatsActionCallback
from app.bot.callbacks.tasks import TaskActionCallback


def main_menu_keyboard() -> InlineKeyboardMarkup:
    add_task = TaskActionCallback(action='add', task_id=0).pack()
    stats = StatsActionCallback(action='open').pack()
    backlog = BacklogActionCallback(action='open').pack()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='➕ Добавить задачу',
                                  callback_data=add_task)],
            [InlineKeyboardButton(text='📅 Беклог', callback_data=backlog)],
            [InlineKeyboardButton(text='📊 Статистика', callback_data=stats)],
        ],
    )
