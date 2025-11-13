from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.service.take_spot_service import take_spot


async def handle_take_spot(query: CallbackQuery, state: FSMContext):
    """Обрабатывает подтверждение занятия места"""
    await take_spot(query, state)