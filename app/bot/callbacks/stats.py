from aiogram.filters.callback_data import CallbackData


class StatsActionCallback(CallbackData, prefix='stats'):
    action: str
