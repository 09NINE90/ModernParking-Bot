from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.keyboard_markup import create_default_schedule_markup


async def handle_add_day(query: CallbackQuery, state: FSMContext, day: str):
    data = await state.get_data()
    selected_days = data.get('selected_days', [])

    if day not in selected_days:
        selected_days.append(day)
        await state.update_data(selected_days=selected_days)

    await update_schedule_message(query, state)


async def update_schedule_message(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_days = data.get('selected_days', [])

    if selected_days:
        days_text = ", ".join(selected_days)
        message_text = (f"Выбранные дни: <b>{days_text}</b>\n\nПродолжайте выбирать дни или:\n"
                        f"• Нажмите <b>'🔙 Назад'</b> для отмены заполнения расписания.\n"
                        f"• Нажмите <b>'💾 Сохранить'</b> для перехода к утверждению расписания")
    else:
        message_text = "Выберите дни недели:"

    await query.message.edit_text(
        text=message_text,
        reply_markup=create_default_schedule_markup(selected_days)
    )
