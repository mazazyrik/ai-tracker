from aiogram.filters.callback_data import CallbackData


class AiActionCallback(CallbackData, prefix='ai'):
    action: str
