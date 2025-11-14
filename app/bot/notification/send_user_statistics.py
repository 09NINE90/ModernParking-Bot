import logging

from aiogram.types import CallbackQuery

from app.bot.keyboard_markup import return_markup


async def send_user_statistics(query: CallbackQuery, message: str):
    """Отправляет пользователю его актуальную статистику о распределении мест"""
    try:
        message_text = (
            f"👋<b>Привет!</b>\n"
            f"{message}"
        )

        await query.message.edit_text(text=message_text,
                                      reply_markup=return_markup)
        return True
    except Exception as e:
        logging.error(f"Error sending statistics to user: {e}")
        return False
