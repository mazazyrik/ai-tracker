from aiogram.filters.callback_data import CallbackData


class TaskActionCallback(CallbackData, prefix='task'):
    action: str
    task_id: int


class TimerActionCallback(CallbackData, prefix='timer'):
    action: str
    task_id: int
