import logging

from app.bot.constants.log_types import LogNotification
from app.bot.notification.log_notification import send_log_notification
from app.bot.notification.messages.to_user_about_time_confirmation_spent_by_reminder import \
    to_user_about_time_confirmation_spent_by_reminder
from app.bot.notification.notify_user import notify_user
from app.bot.service.reminder_spot.process_confirmation_spot_by_reminder_service import process_spot_cancel_by_reminder
from app.data.models.spot_reminder.parking_reminder_dto import ParkingReminder
from app.log_text import AUTO_CANCEL_SPOT_FAILED, AUTO_CANCEL_SPOT_ERROR


async def auto_cancel_reminder(reminder_data: ParkingReminder):
    """
        Автоматически отменяет место если пользователь не подтвердил вовремя
    """
    try:
        logging.debug(f"Auto-canceling spot for user {reminder_data.user_tg_id}, "
                     f"spot №{reminder_data.spot_id} on {reminder_data}")

        success = await process_spot_cancel_by_reminder(reminder_data)

        if success:
            message_text = await to_user_about_time_confirmation_spent_by_reminder(reminder_data)
            await notify_user(reminder_data.user_tg_id, message_text)

            from app.bot.service.distribution_service import distribute_parking_spots
            await distribute_parking_spots()
        else:
            logging.error(AUTO_CANCEL_SPOT_FAILED.format(reminder_data.user_tg_id))

    except Exception as e:
        logging.error(AUTO_CANCEL_SPOT_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, AUTO_CANCEL_SPOT_ERROR.format(e))
