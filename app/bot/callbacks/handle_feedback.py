import html
import logging

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.constants.log_types import LogNotification
from app.bot.keyboard_markup import return_markup
from app.bot.notification.log_notification import send_log_notification
from app.bot.notification.send_feedback import send_feedback
from app.bot.parking_states import ParkingStates
from app.log_text import FEEDBACK_SEND_ERROR, FEEDBACK_HANDLE_ERROR


async def handle_feedback(query: CallbackQuery, state: FSMContext, feedback_type):
    """Обработка выбора типа фидбека"""
    message_texts = {
        "error": "Опишите проблему:",
        "idea": "Распишите свою идею:",
        "feedback": "Напишите отзыв:"
    }

    message_text = message_texts.get(feedback_type, "Напишите ваше сообщение:")

    try:
        await query.message.edit_text(
            text=message_text,
            reply_markup=return_markup
        )
        await state.set_state(ParkingStates.waiting_for_feedback)
        await state.update_data(feedback_type=feedback_type)
    except Exception as e:
        logging.error(FEEDBACK_HANDLE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, FEEDBACK_HANDLE_ERROR.format(e))
        await query.message.answer("Произошла ошибка, попробуйте снова")


async def handle_write_feedback(message: types.Message, state: FSMContext):
    feedback = message.text.strip()

    if not feedback:
        await message.answer("Сообщение не может быть пустым. Попробуйте еще раз:")
        return

    if len(feedback) > 1500:
        await message.answer("Сообщение слишком длинное. Максимум 4000 символов.")
        return

    safe_feedback = html.escape(feedback)

    await state.update_data(feedback_message=safe_feedback)

    try:
        await send_feedback(message, state)
        await state.clear()
    except Exception as e:
        logging.error(FEEDBACK_SEND_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, FEEDBACK_SEND_ERROR.format(e))
        await message.answer("Произошла ошибка при отправке отзыва. Попробуйте позже.")

