from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.service.release.revoke_release_service import show_revoke_release_keyboard


async def handle_show_revoke_release_keyboard(query: CallbackQuery, state: FSMContext):
    await show_revoke_release_keyboard(query, state)