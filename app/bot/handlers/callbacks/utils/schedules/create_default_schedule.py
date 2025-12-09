from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot import ParkingStates
from app.bot.keyboards import create_default_schedule_markup


async def create_default_schedule(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ParkingStates.waiting_for_days)
    await state.update_data(selected_days=[])

    await callback.message.edit_text(
        text="📅 <b>Настройте регулярное расписание</b>\n\n"
             "Выберите дни, когда вам нужно занимать места:\n\n"
             "🔔 <i>Каждое воскресенье я буду уточнять, нужно ли создавать брони на выбранные дни</i>",
        reply_markup=create_default_schedule_markup()
    )