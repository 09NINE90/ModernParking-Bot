import logging

from app.bot.config import bot
from app.bot.constants.log_types import LogNotification
from app.bot.notification.log_notification import send_log_notification
from app.log_text import WEEKLY_STATISTICS_SEND_ERROR


async def weekly_statistics_notification(tg_chat_id: int, message: str, monday_date, friday_date):
    """Отправляет уведомление о статистеке распределения мест за текущую неделю"""
    try:
        message_text = (
            f"👋<b>Всем привет!</b>\n"
            f"<b>📊 Статистика за текущую неделю</b> <u>{monday_date.strftime('%d.%m.%Y')}-{friday_date.strftime('%d.%m.%Y')}</u>:\n"
            f"{message}"
        )

        try:
            await bot.get_chat(tg_chat_id)
        except Exception as e:
            logging.error(f"Нет доступа к чату {tg_chat_id}: {e}")
            return False

        await bot.send_message(
            chat_id=tg_chat_id,
            text=message_text
        )
        return True
    except Exception as e:
        logging.error(WEEKLY_STATISTICS_SEND_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, WEEKLY_STATISTICS_SEND_ERROR.format(e))
        return False

