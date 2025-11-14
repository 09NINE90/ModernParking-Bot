import logging
from app.data.init_db import get_db_connection
from app.data.models.parking_releases import ParkingReleaseStatus
from app.data.models.parking_requests import ParkingRequestStatus
from app.data.repository.distribute_parking_spots_repository import (
    update_parking_releases, update_parking_request_status,
    update_user_rating, get_release_owner
)
from app.bot.notification.notify_owner_about_taken_spot import notify_owner_about_taken_spot


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
                    await notify_owner_about_taken_spot(release_tg_id, spot_number, assignment_date)

                conn.commit()
                return True

    except Exception as e:
        logging.error(f"Error processing spot confirmation: {e}")
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
                conn.commit()
                return True

    except Exception as e:
        logging.error(f"Error processing spot cancel: {e}")
        return False