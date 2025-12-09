from aiogram.filters.callback_data import CallbackData


class MenuActionCallback(CallbackData, prefix='menu'):
    action: str
