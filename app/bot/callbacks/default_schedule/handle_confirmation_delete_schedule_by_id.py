from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.service.user_schedules.delete_schedule_service import confirmation_delete_schedule_by_id


async def handle_confirmation_delete_schedule_by_id(query: CallbackQuery, state: FSMContext, schedule_id: str):
    await confirmation_delete_schedule_by_id(query, state, schedule_id)
