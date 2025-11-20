from datetime import date

from app.data.models.requests.requests_enum import ParkingRequestStatus
from app.data.models.requests.revoke_requests_dto import RevokeRequest
from app.data.repository.parking_requests_repository import update_parking_request_status
from app.data.repository.parking_requests_repository import find_user_requests_for_revoke, \
    find_request_for_confirm_revoke


async def get_user_requests_for_revoke(cur, db_user_id):
    today = date.today()
    results = await find_user_requests_for_revoke(cur, db_user_id, today)
    if not results:
        return None
    return [RevokeRequest(
        request_id=row[0],
        request_date=row[1],
        status=ParkingRequestStatus(row[2]),
        spot_id=row[3],
    ) for row in results]


async def get_request_for_confirm_revoke(cur, request_id, db_user_id):
    result = await find_request_for_confirm_revoke(cur, db_user_id, request_id)
    if not result:
        return None
    return RevokeRequest(
        request_id=result[0],
        request_date=result[1],
        status=ParkingRequestStatus(result[2]),
        spot_id=result[3],
        release_id=result[4]
    )


async def update_request_status(cur, request_id, status):
    await update_parking_request_status(cur, request_id, status)