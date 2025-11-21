from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.service.reminder_spot.take_spot_by_reminder import take_spot_by_reminder


async def handle_take_spot_by_reminder(query: CallbackQuery, state: FSMContext):
    await take_spot_by_reminder(query)