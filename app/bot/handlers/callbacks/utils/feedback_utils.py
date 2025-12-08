import html
from datetime import datetime

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot import ParkingStates
from app.bot.keyboards import back_to_main_markup
from app.bot.utils import get_user_full_mention
from app.config import settings
from app.logs.log_builder import log


async def processing_feedback(callback: CallbackQuery, state: FSMContext, feedback_type):
    """Обработка выбора типа фидбека"""

    message_texts = {
        "error": "Опишите проблему:",
        "idea": "Распишите свою идею:",
        "feedback": "Напишите отзыв:"
    }

    message_text = message_texts.get(feedback_type, "Напишите ваше сообщение:")

    await callback.message.edit_text(
        text=message_text,
        reply_markup=back_to_main_markup
    )
    await state.set_state(ParkingStates.waiting_for_feedback)
    await state.update_data(feedback_type=feedback_type)


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

    await send_feedback(message, state)


async def send_feedback(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        feedback_type = data.get('feedback_type', 'unknown')
        feedback_message = data.get('feedback_message', '')
        user_id = message.from_user.id

        type_display = {
            "error": "🚨 Проблема",
            "idea": "💡 Идея",
            "feedback": "📝 Отзыв",
            "unknown": "❓ Неизвестно"
        }.get(feedback_type, "❓ Неизвестно")

        user_info = await get_user_full_mention(user_id=user_id, is_link=True)

        message_text = (
            f"{type_display}\n\n"
            f"💬 Сообщение:\n{feedback_message}\n\n"
            f"👤 Пользователь:\n{user_info}\n"
            f"📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )

        from app.bot import bot
        sent_message = await bot.send_message(
            chat_id=settings.TECH_GROUP_ID,
            message_thread_id=settings.FEEDBACK_TOPIC_ID,
            text=message_text
        )

        if sent_message:
            await message.answer(
                text="✅ Ваш отзыв успешно отправлен! Спасибо!",
                reply_markup=back_to_main_markup
            )

        await state.clear()
        return True

    except Exception as e:
        await log(
            log_message=f"Ошибка отправки отзыва: {e}"
        )

        await message.answer("❌ Произошла ошибка при отправке отзыва. Попробуйте позже.")

        return False
