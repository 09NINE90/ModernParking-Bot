from datetime import date

from app.data import get_db_connection
from app.services import ServiceFactory


async def update_statuses():
    today = date.today()

    with get_db_connection() as conn:
        spot_release_service = ServiceFactory.create_spot_release_service(conn)
        spot_request_service = ServiceFactory.create_spot_request_service(conn)

        spot_request_service.update_requests_statuses_to_not_found_by_date(
            rq_date=today,
        )
        spot_release_service.update_releases_statuses_to_not_found_by_date(
            rq_date=today,
        )

        conn.commit()