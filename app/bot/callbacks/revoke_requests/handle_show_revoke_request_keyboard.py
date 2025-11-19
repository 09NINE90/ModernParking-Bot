from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.service.requests.revoke_request_service import show_revoke_request_keyboard


async def handle_show_revoke_request_keyboard(query: CallbackQuery, state: FSMContext):
    await show_revoke_request_keyboard(query, state)