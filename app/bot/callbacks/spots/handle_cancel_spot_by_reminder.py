from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.service.reminder_spot.cancel_spot_by_reminder import cancel_spot_by_reminder


async def handle_cancel_spot_by_reminder(query: CallbackQuery, state: FSMContext):
    await cancel_spot_by_reminder(query)