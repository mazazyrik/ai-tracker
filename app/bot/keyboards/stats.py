from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.callbacks.menu import MenuActionCallback
from app.bot.callbacks.stats import StatsActionCallback


def stats_menu_keyboard() -> InlineKeyboardMarkup:
    daily = StatsActionCallback(action='daily').pack()
    weekly = StatsActionCallback(action='weekly').pack()
    back_menu = MenuActionCallback(action='main').pack()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='📅 За сегодня', callback_data=daily)],
            [InlineKeyboardButton(text='📈 За неделю', callback_data=weekly)],
            [InlineKeyboardButton(text='⬅️ В меню', callback_data=back_menu)],
        ],
    )
