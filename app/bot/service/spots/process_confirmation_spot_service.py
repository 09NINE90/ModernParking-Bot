import logging

import psycopg2

from app.bot.constants.log_types import LogNotification
from app.bot.notification.log_notification import send_log_notification
from app.bot.service.requests.request_service import update_request_status
from app.data.models.releases.parking_releases import ParkingReleaseStatus
from app.data.models.requests.parking_requests import ParkingRequestStatus
from app.data.repository.parking_releases_repository import update_parking_releases, get_release_owner
from app.data.repository.spot_confirmations_repository import deactivate_spot_confirmations_by_user
from app.log_text import SPOT_CANCEL_PROCESSING_ERROR, DATABASE_ERROR


async def process_spot_cancel(cur, confirmation_data) -> bool:
    """Обрабатывает отмену места"""
    request_id = confirmation_data.request_id
    release_id = confirmation_data.release_id
    db_user_id = confirmation_data.db_user_id

    try:
        await update_parking_releases(cur, db_user_id, release_id, ParkingReleaseStatus.PENDING)
        await update_request_status(cur, request_id, ParkingRequestStatus.CANCELED)
        await deactivate_spot_confirmations_by_user(cur, db_user_id)
        return True

    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))
        return False
    except Exception as e:
        logging.error(SPOT_CANCEL_PROCESSING_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, SPOT_CANCEL_PROCESSING_ERROR.format(e))
        return False
