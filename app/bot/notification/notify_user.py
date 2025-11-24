import logging

from app.bot.config import bot
from app.bot.constants.log_types import LogNotification
from app.bot.keyboard_markup import return_markup, found_spot_markup, reminder_spot_confirmation_markup
from app.bot.notification.log_notification import send_log_notification
from app.bot.notification.types_notifications import NotificationTypes
from app.log_text import USER_NOTIFICATION_ERROR


async def notify_user(tg_user_id: int, message_text, notification_type: NotificationTypes = NotificationTypes.BASE):
    """Отправляет уведомление пользователю"""
    if notification_type == NotificationTypes.SPOT_FOUND:
        markup = found_spot_markup
    elif notification_type == NotificationTypes.SPOT_REMINDER:
        markup = reminder_spot_confirmation_markup
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
