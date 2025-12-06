from app.bot.keyboards import back_to_main_markup, found_spot_markup, reminder_spot_confirmation_markup
from app.bot.notification.enumz import NotificationTypes
from app.logs.log_builder import log


async def notify_user(tg_user_id: int, message_text, notification_type: NotificationTypes = NotificationTypes.BASE):
    """Отправляет уведомление пользователю"""

    markup = back_to_main_markup
    if notification_type == NotificationTypes.SPOT_FOUND:
        markup = found_spot_markup
    elif notification_type == NotificationTypes.SPOT_REMINDER:
        markup = reminder_spot_confirmation_markup

    try:
        from app.bot import bot
        sent_message = await bot.send_message(
            chat_id=tg_user_id,
            text=message_text,
            reply_markup=markup
        )
        return sent_message.message_id
    except Exception as e:
        await log(log_message=f"Ошибка отправки сообщения пользователю {tg_user_id}: {e}")
        return False
