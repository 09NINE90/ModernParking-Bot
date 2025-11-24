import logging

import psycopg2

from app.bot.constants.log_types import LogNotification
from app.bot.notification.log_notification import send_log_notification
from app.bot.service.requests.request_service import update_request_status
from app.data.init_db import get_db_connection
from app.data.models.releases.releases_enum import ParkingReleaseStatus
from app.data.models.requests.requests_enum import ParkingRequestStatus
from app.data.models.spot_reminder.parking_reminder_dto import ParkingReminder
from app.data.repository.parking_releases_repository import update_parking_releases
from app.data.repository.reminder_spot_confirmations_repository import deactivate_reminder_spot_confirmations_by_user
from app.log_text import DATABASE_ERROR, SPOT_CANCEL_PROCESSING_ERROR


async def process_spot_cancel_by_reminder(reminder_data: ParkingReminder):
    request_id = reminder_data.request_id
    release_id = reminder_data.release_id
    db_user_id = reminder_data.db_user_id

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                await update_parking_releases(cur, db_user_id, release_id, ParkingReleaseStatus.PENDING)
                await update_request_status(cur, request_id, ParkingRequestStatus.CANCELED)
                await deactivate_reminder_spot_confirmations_by_user(cur, db_user_id)
                conn.commit()
                return True

    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))
        return False
    except Exception as e:
        logging.error(SPOT_CANCEL_PROCESSING_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, SPOT_CANCEL_PROCESSING_ERROR.format(e))
        return False