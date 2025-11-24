import logging
from datetime import date, timedelta

import psycopg2

from app.bot.constants.log_types import LogNotification
from app.bot.notification.log_notification import send_log_notification
from app.bot.notification.messages.to_remind_user_of_spot import to_remind_user_of_spot
from app.bot.notification.notify_user import notify_user
from app.bot.notification.types_notifications import NotificationTypes
from app.data.init_db import get_db_connection
from app.data.models.spot_reminder.parking_reminder_dto import ParkingReminder
from app.data.repository.parking_releases_repository import get_tomorrow_accepted_spot
from app.data.repository.reminder_spot_confirmations_repository import insert_row_of_reminder_spot_confirmations
from app.log_text import SPOT_REMINDER_ERROR, DATABASE_ERROR


async def spot_reminder():
    """
        Асинхронная функция для отправки напоминаний пользователям о парковочных местах на завтра.
    """
    try:
        tomorrow = date.today() + timedelta(days=1)
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                results = await get_tomorrow_accepted_spot(cur, tomorrow)

                current_spots_releases = [ParkingReminder(
                    spot_id=row[0],
                    user_tg_id=row[1],
                    db_user_id=row[2],
                    release_id=row[3],
                    release_date=row[4],
                    request_id=row[5]
                )
                    for row in results]

                if len(current_spots_releases) > 0:
                    for release in current_spots_releases:
                        await insert_row_of_reminder_spot_confirmations(cur, release.db_user_id, release.release_id, release.request_id)
                        message_text = await to_remind_user_of_spot(release)
                        await notify_user(release.user_tg_id, message_text, NotificationTypes.SPOT_REMINDER)

    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))
    except Exception as e:
        logging.error(SPOT_REMINDER_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, SPOT_REMINDER_ERROR.format(e))
