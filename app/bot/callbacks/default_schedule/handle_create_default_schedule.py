from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.keyboard_markup import create_default_schedule_markup
from app.bot.parking_states import ParkingStates


async def handle_create_default_schedule(query: CallbackQuery, state: FSMContext):
    await state.set_state(ParkingStates.waiting_for_days)
    await state.update_data(selected_days=[])

    await query.message.edit_text(
        text="📅 <b>Настройте регулярное расписание</b>\n\n"
             "Выберите дни, когда вам нужно занимать места:\n\n"
             "🔔 <i>Каждое воскресенье я буду уточнять, нужно ли создавать брони на выбранные дни</i>",
        reply_markup=create_default_schedule_markup()
    )