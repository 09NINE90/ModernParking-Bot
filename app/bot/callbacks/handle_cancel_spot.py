from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.service.cancel_spot_service import cancel_spot


async def handle_cancel_spot(query: CallbackQuery, state: FSMContext):
    """Обрабатывает отмену занятия места"""
    await cancel_spot(query, state)
