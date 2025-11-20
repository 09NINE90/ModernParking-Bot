import logging

from aiogram.types import CallbackQuery

from app.bot.constants.log_types import LogNotification
from app.bot.keyboard_markup import return_markup
from app.bot.notification.log_notification import send_log_notification
from app.log_text import STATISTICS_SEND_ERROR


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
        logging.error(STATISTICS_SEND_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, STATISTICS_SEND_ERROR.format(e))
        return False
