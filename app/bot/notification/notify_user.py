import logging

from app.bot.config import bot
from app.bot.constants.log_types import LogNotification
from app.bot.keyboard_markup import return_markup, found_spot_markup
from app.bot.notification.log_notification import send_log_notification
from app.log_text import USER_NOTIFICATION_ERROR


async def notify_user(tg_user_id: int, message_text, is_found_spot: bool = False):
    """Отправляет уведомление пользователю"""
    if is_found_spot:
        markup = found_spot_markup
    else:
        markup = return_markup

    try:
        await bot.send_message(
            chat_id=tg_user_id,
            text=message_text,
            reply_markup=markup
        )
        return True
    except Exception as e:
        logging.error(USER_NOTIFICATION_ERROR.format(tg_user_id, e))
        await send_log_notification(LogNotification.ERROR, USER_NOTIFICATION_ERROR.format(tg_user_id, e))
        return False
