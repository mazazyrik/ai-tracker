from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.callbacks.ai import AiActionCallback
from app.bot.callbacks.menu import MenuActionCallback


def ai_menu_keyboard() -> InlineKeyboardMarkup:
    daily = AiActionCallback(action='daily').pack()
    weekly = AiActionCallback(action='weekly').pack()
    back_menu = MenuActionCallback(action='main').pack()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🤖 Саммари дня', callback_data=daily)],
            [InlineKeyboardButton(text='📘 Отчёт за неделю', callback_data=weekly)],
            [InlineKeyboardButton(text='⬅️ В меню', callback_data=back_menu)],
        ],
    )


