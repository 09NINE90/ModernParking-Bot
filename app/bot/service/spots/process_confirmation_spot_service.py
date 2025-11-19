import logging

import psycopg2

from app.bot.constants.log_types import LogNotification
from app.bot.notification.log_notification import send_log_notification
from app.bot.notification.messages.to_owner_message import to_owner_message
from app.bot.notification.notify_user import notify_user
from app.data.init_db import get_db_connection
from app.data.models.releases.parking_releases import ParkingReleaseStatus
from app.data.models.requests.parking_requests import ParkingRequestStatus
from app.data.repository.distribute_parking_spots_repository import (
    update_parking_releases, update_parking_request_status,
    update_user_rating, get_release_owner
)
from app.data.repository.spot_confirmations_repository import deactivate_spot_confirmations_by_user
from app.log_text import SPOT_CONFIRMATION_PROCESSING_ERROR, SPOT_CANCEL_PROCESSING_ERROR, DATABASE_ERROR


async def process_spot_confirmation(confirmation_data) -> bool:
    """Обрабатывает подтверждение места"""
    spot_number = confirmation_data.spot_number
    assignment_date = confirmation_data.assignment_date
    request_id = confirmation_data.request_id
    release_id = confirmation_data.release_id
    db_user_id = confirmation_data.db_user_id

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                await update_parking_releases(cur, db_user_id, release_id, ParkingReleaseStatus.ACCEPTED)
                await update_parking_request_status(cur, request_id, ParkingRequestStatus.ACCEPTED)
                await update_user_rating(cur, db_user_id)

                release_owner = await get_release_owner(cur, release_id)
                if release_owner:
                    release_user_id, release_tg_id = release_owner
                    message_text = await to_owner_message(release_tg_id, spot_number, assignment_date)
                    await notify_user(release_tg_id, message_text)
                conn.commit()
                return True

    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))
    except Exception as e:
        logging.error(SPOT_CONFIRMATION_PROCESSING_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, SPOT_CONFIRMATION_PROCESSING_ERROR.format(e))
        return False


async def process_spot_cancel(confirmation_data) -> bool:
    """Обрабатывает отмену места"""
    request_id = confirmation_data.request_id
    release_id = confirmation_data.release_id
    db_user_id = confirmation_data.db_user_id

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                await update_parking_releases(cur, db_user_id, release_id, ParkingReleaseStatus.PENDING)
                await update_parking_request_status(cur, request_id, ParkingRequestStatus.CANCELED)
                await deactivate_spot_confirmations_by_user(cur, db_user_id)
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