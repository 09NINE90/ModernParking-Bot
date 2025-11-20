import logging

from app.bot.config import bot
from app.bot.constants.log_types import LogNotification
from app.bot.notification.log_notification import send_log_notification
from app.bot.service.chat_access_required_service import chat_access_required
from app.bot.service.unpin_pin_message_service import pin_last_message, unpin_last_message
from app.log_text import WEEKLY_STATISTICS_SEND_ERROR, CHAT_ACCESS_ERROR


@chat_access_required
async def weekly_statistics_notification(tg_chat_id: int, message: str, monday_date, friday_date, is_pinned=False):
    """Отправляет уведомление о статистеке распределения мест за текущую неделю"""
    try:
        message_text = (
            f"👋<b>Всем привет!</b>\n"
            f"<b>📊 Статистика за текущую неделю</b> <u>{monday_date.strftime('%d.%m.%Y')}-{friday_date.strftime('%d.%m.%Y')}</u>:\n"
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
        logging.error(WEEKLY_STATISTICS_SEND_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, WEEKLY_STATISTICS_SEND_ERROR.format(e))
        return False