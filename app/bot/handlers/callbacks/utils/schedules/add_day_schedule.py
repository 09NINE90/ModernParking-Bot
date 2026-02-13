from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.keyboards import create_default_schedule_markup
from app.utils.emoji_util import back_emoji, save_emoji, sber_back_emoji


async def add_day_schedule(callback, state, day):
    data = await state.get_data()
    selected_days = data.get('selected_days', [])

    if day not in selected_days:
        selected_days.append(day)
        await state.update_data(selected_days=selected_days)

    await update_schedule_message(callback, state)


async def update_schedule_message(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_days = data.get('selected_days', [])

    if selected_days:
        days_text = ", ".join(selected_days)
        message_text = (f"Выбранные дни: <b>{days_text}</b>\n\nПродолжайте выбирать дни или:\n"
                        f"• Нажмите <b>'{sber_back_emoji} Назад'</b> для отмены заполнения расписания.\n"
                        f"• Нажмите <b>'{save_emoji} Сохранить'</b> для перехода к утверждению расписания")
    else:
        message_text = "Выберите дни недели:"

    await callback.message.edit_text(
        text=message_text,
        reply_markup=create_default_schedule_markup(selected_days)
    )
