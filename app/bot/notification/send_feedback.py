import logging
from datetime import datetime

from aiogram import types
from aiogram.fsm.context import FSMContext

from app.bot.config import FEEDBACK_CHANNEL_ID, bot
from app.bot.constants.log_types import LogNotification
from app.bot.keyboard_markup import return_markup
from app.bot.notification.log_notification import send_log_notification
from app.bot.users.get_user_full_mention import get_user_full_mention
from app.log_text import FEEDBACK_MESSAGE_PROCESSING_ERROR


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
            f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        sent_message = await bot.send_message(
            chat_id=FEEDBACK_CHANNEL_ID,
            text=message_text
        )

        if sent_message:
            await message.answer(
                text="✅ Ваш отзыв успешно отправлен! Спасибо!",
                reply_markup=return_markup
            )

        return True

    except Exception as e:
        logging.error(FEEDBACK_MESSAGE_PROCESSING_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, FEEDBACK_MESSAGE_PROCESSING_ERROR.format(e))

        await message.answer("❌ Произошла ошибка при отправке отзыва. Попробуйте позже.")

        return False
