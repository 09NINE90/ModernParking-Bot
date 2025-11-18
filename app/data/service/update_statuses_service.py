import logging
from datetime import date

from app.bot.constants.log_types import LogNotification
from app.bot.notification.log_notification import send_log_notification
from app.data.init_db import get_db_connection
from app.data.models.parking_releases import ParkingReleaseStatus
from app.data.models.parking_requests import ParkingRequestStatus
from app.log_text import STATUS_UPDATE_ERROR


async def update_statuses_service():
    today = date.today()
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                            UPDATE dont_touch.parking_releases
                            SET status = %s
                            WHERE status = %s
                                AND release_date < %s
                            ''', (ParkingReleaseStatus.NOT_FOUND.value, ParkingReleaseStatus.PENDING.name, today))

                cur.execute('''
                            UPDATE dont_touch.parking_requests
                            SET status = %s
                            WHERE status = %s
                              AND request_date < %s
                            ''', (ParkingRequestStatus.NOT_FOUND.value, ParkingRequestStatus.PENDING.name, today))
    except Exception as e:
        logging.error(STATUS_UPDATE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, STATUS_UPDATE_ERROR.format(e))
        return