import logging
from datetime import date, timedelta

from app.bot.constants.log_types import LogNotification
from app.bot.notification.log_notification import send_log_notification
from app.bot.notification.messages.to_remind_user_of_spot import to_remind_user_of_spot
from app.bot.notification.notify_user import notify_user
from app.data.init_db import get_db_connection
from app.data.models.parking_reminder import ParkingReminder
from app.data.repository.parking_releases_repository import get_tomorrow_accepted_spot
from app.log_text import SPOT_REMINDER_ERROR


async def spot_reminder():
    """
        Асинхронная функция для отправки напоминаний пользователям о парковочных местах на завтра.
    """
    try:
        tomorrow = date.today() + timedelta(days=1)
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                results = await get_tomorrow_accepted_spot(cur, tomorrow)

                current_spots_releases = [ParkingReminder(spot_id=row[0], user_tg_id=row[1])
                                          for row in results]

                if len(current_spots_releases) > 0:
                    for spot in current_spots_releases:
                        message_text = await to_remind_user_of_spot(spot.spot_id)
                        await notify_user(spot.user_tg_id, message_text)

    except Exception as e:
        logging.error(SPOT_REMINDER_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, SPOT_REMINDER_ERROR.format(e))