import logging
from datetime import date

import psycopg2

from app.bot.constants.log_types import LogNotification
from app.bot.notification.log_notification import send_log_notification
from app.data.db_config import DB_SCHEMA
from app.data.init_db import get_db_connection
from app.data.models.releases.parking_releases import ParkingReleaseStatus
from app.data.models.requests.parking_requests import ParkingRequestStatus
from app.log_text import STATUS_UPDATE_ERROR, DATABASE_ERROR


async def update_statuses_service():
    today = date.today()
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f'''
                            UPDATE {DB_SCHEMA}.parking_releases
                            SET status = %s
                            WHERE status = %s
                                AND release_date < %s
                            ''', (ParkingReleaseStatus.NOT_FOUND.value, ParkingReleaseStatus.PENDING.name, today))

                cur.execute(f'''
                            UPDATE {DB_SCHEMA}.parking_requests
                            SET status = %s
                            WHERE status = %s
                              AND request_date < %s
                            ''', (ParkingRequestStatus.NOT_FOUND.value, ParkingRequestStatus.PENDING.name, today))
    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))
    except Exception as e:
        logging.error(STATUS_UPDATE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, STATUS_UPDATE_ERROR.format(e))
        return