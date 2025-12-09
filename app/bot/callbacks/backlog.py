from aiogram.filters.callback_data import CallbackData


class BacklogActionCallback(CallbackData, prefix='backlog'):
    action: str


class BacklogDayCallback(CallbackData, prefix='backlog_day'):
    day: str


