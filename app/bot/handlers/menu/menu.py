from datetime import date

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from app.bot.callbacks.menu import MenuActionCallback
from app.bot.keyboards.menu import main_menu_keyboard
from app.bot.keyboards.tasks import tasks_list_keyboard
from app.core.logger import get_logger
from app.db.models.user import User
from app.services.tasks_service import list_active_or_planned_for_today


logger = get_logger('menu_handlers')

menu_router = Router()


async def _show_main_menu(message: Message, user: User) -> None:
    today = date.today()
    tasks = await list_active_or_planned_for_today(user, today)
    logger.info('show_main_menu user_id=%s tasks=%s', user.id, len(tasks))
    if tasks:
        lines = ['📅 Задачи на сегодня:']
        for idx, t in enumerate(tasks, start=1):
            lines.append(f'{idx}. {t.title} — {t.planned_seconds // 60} мин')
        text = '\n'.join(lines)
        await message.answer(text, reply_markup=tasks_list_keyboard(tasks))
    else:
        await message.answer('📅 Задач на сегодня нет.', reply_markup=main_menu_keyboard())


@menu_router.message(CommandStart())
async def cmd_start(message: Message, user: User) -> None:
    await _show_main_menu(message, user)


@menu_router.callback_query(MenuActionCallback.filter(F.action == 'main'))
async def menu_main(callback: CallbackQuery, user: User) -> None:
    await callback.message.edit_text('⬇️ Задачи на сегодня')
    await _show_main_menu(callback.message, user)
    await callback.answer()
