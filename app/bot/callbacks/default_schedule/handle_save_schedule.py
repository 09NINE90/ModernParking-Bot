from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.service.user_schedules.save_schedule_service import save_schedule


async def handle_save_schedule(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_days = data.get('selected_days', [])
    await save_schedule(query, state, selected_days)