from aiogram.fsm.state import State, StatesGroup


class AddTaskStates(StatesGroup):
    title = State()
    planned_time = State()


class AddFutureTaskStates(StatesGroup):
    title = State()
    planned_time = State()
    date = State()


class ExtendTaskStates(StatesGroup):
    minutes = State()


class EditTaskTimeStates(StatesGroup):
    new_time = State()


class TaskScoreStates(StatesGroup):
    score = State()


class ConfirmStates(StatesGroup):
    confirm = State()


