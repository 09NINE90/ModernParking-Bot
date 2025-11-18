import logging
from datetime import datetime

from app.bot.config import bot
from app.bot.constants.log_types import LogNotification
from app.bot.notification.log_notification import send_log_notification
from app.log_text import USER_NOTIFICATION_ERROR


async def daily_statistics_notification(tg_chat_id: int, message: str, assignment_date):
    """Отправляет уведомление пользователю о назначении места"""
    day_text = get_day_text(assignment_date)

    try:
        message_text = (
            f"👋<b>Всем привет!</b>\n"
            f"📊 Ситуация на {day_text} <u>{assignment_date.strftime('%d.%m.%Y')}</u>:\n"
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
        logging.error(USER_NOTIFICATION_ERROR.format(tg_chat_id, e))
        await send_log_notification(LogNotification.ERROR, USER_NOTIFICATION_ERROR.format(tg_chat_id, e))
        return False


def get_day_text(assignment_date):
    if datetime.today().date() == assignment_date:
        return "сегодня"
    else:
        return "завтра"
