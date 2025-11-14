import logging
from datetime import date

from app.data.init_db import get_db_connection
from app.data.models.parking_releases import ParkingReleaseStatus
from app.data.models.parking_requests import ParkingRequestStatus


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
                            ''', (ParkingReleaseStatus.NOT_FOUND.value, ParkingReleaseStatus.PENDING.value, today))

                cur.execute('''
                            UPDATE dont_touch.parking_requests
                            SET status = %s
                            WHERE status = %s
                              AND request_date < %s
                            ''', (ParkingRequestStatus.NOT_FOUND.value, ParkingRequestStatus.PENDING.value, today))
    except Exception as e:
        logging.error(f"Error update statuses: {e}")
        return