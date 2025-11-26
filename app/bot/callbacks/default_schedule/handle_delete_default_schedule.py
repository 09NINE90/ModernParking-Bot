from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.service.user_schedules.delete_schedule_service import delete_default_schedule


async def handle_delete_default_schedule(query: CallbackQuery, state: FSMContext):
    await delete_default_schedule(query, state)