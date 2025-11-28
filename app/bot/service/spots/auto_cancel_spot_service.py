import logging

import psycopg2

from app.bot.constants.log_types import LogNotification
from app.bot.notification.log_notification import send_log_notification
from app.bot.notification.messages.to_user_about_time_confirmation_spent import to_user_about_time_confirmation_spent
from app.bot.notification.notify_user import notify_user
from app.bot.service.spots.process_confirmation_spot_service import process_spot_cancel
from app.data.init_db import get_db_connection
from app.log_text import AUTO_CANCEL_SPOT_ERROR, AUTO_CANCEL_SPOT_FAILED, DATABASE_ERROR


async def auto_cancel_spot(confirmation_data):
    """
        Автоматически отменяет место если пользователь не подтвердил вовремя
    """
    try:
        logging.debug(f"Auto-canceling spot for user {confirmation_data.tg_user_id}, "
                     f"spot №{confirmation_data.spot_number} on {confirmation_data.assignment_date}")

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    success = await process_spot_cancel(cur, confirmation_data)

                    if success:
                        message_text = await to_user_about_time_confirmation_spent(confirmation_data)
                        await notify_user(confirmation_data.tg_user_id, message_text)

                        from app.bot.service.distribution_service import distribute_parking_spots
                        await distribute_parking_spots()
                    else:
                        logging.error(AUTO_CANCEL_SPOT_FAILED.format(confirmation_data.tg_user_id))
        except psycopg2.Error as e:
            logging.error(DATABASE_ERROR.format(e))
            await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))
            return False

    except Exception as e:
        logging.error(AUTO_CANCEL_SPOT_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, AUTO_CANCEL_SPOT_ERROR.format(e))