from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.service.user_schedules.weekly_schedule_reminder_service import select_schedule


async def handle_select_schedule(query: CallbackQuery, state: FSMContext, schedule_id):
    await select_schedule(query, state, schedule_id)