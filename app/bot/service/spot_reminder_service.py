import logging
from datetime import date, timedelta

from app.bot.notification.remind_user_of_spot import remind_user_of_spot
from app.data.init_db import get_db_connection
from app.data.models.parking_reminder import ParkingReminder
from app.data.repository.parking_releases_repository import get_tomorrow_accepted_spot


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
                        await remind_user_of_spot(spot.user_tg_id, spot.spot_id)

    except Exception as e:
        logging.error(f"Error in spot_reminder: {e}")
