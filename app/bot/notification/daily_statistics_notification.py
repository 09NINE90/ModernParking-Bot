import logging
from datetime import datetime

from app.bot.config import bot
from app.bot.constants.log_types import LogNotification
from app.bot.notification.log_notification import send_log_notification
from app.bot.service.chat_access_required_service import chat_access_required
from app.bot.service.unpin_pin_message_service import unpin_last_message, pin_last_message
from app.log_text import USER_NOTIFICATION_ERROR

@chat_access_required
async def daily_statistics_notification(tg_chat_id: int, message: str, assignment_date, is_pinned: bool = False):
    """Отправляет уведомление пользователю о назначении места"""
    day_text = get_day_text(assignment_date)

    try:
        message_text = (
            f"👋<b>Всем привет!</b>\n"
            f"📊 Ситуация на {day_text} <u>{assignment_date.strftime('%d.%m.%Y')}</u>:\n"
            f"{message}"
        )

        # Отправляем новое сообщение
        sent_message = await bot.send_message(
            chat_id=tg_chat_id,
            text=message_text
        )

        if is_pinned:
            # Открепляем предыдущее сообщение бота
            await unpin_last_message(tg_chat_id)
            # Закрепляем новое сообщение
            await pin_last_message(tg_chat_id, sent_message)

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
