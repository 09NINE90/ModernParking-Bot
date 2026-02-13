from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot import ParkingStates
from app.bot.keyboards import create_default_schedule_markup
from app.utils.emoji_util import reminder_emoji, date_emoji, sber_date_emoji


async def create_default_schedule(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ParkingStates.waiting_for_days)
    await state.update_data(selected_days=[])

    await callback.message.edit_text(
        text=f"{sber_date_emoji} <b>Настройте регулярное расписание</b>\n\n"
             "Выберите дни, когда Вам нужно занимать места:\n\n"
             f"{reminder_emoji} <i>Каждое воскресенье я буду уточнять, нужно ли создавать брони на выбранные дни</i>",
        reply_markup=create_default_schedule_markup()
    )