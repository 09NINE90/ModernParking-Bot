from datetime import date

from app.data.models.releases.releases_enum import ParkingReleaseStatus
from app.data.models.releases.revoke_releases_dto import RevokeRelease
from app.data.repository.parking_releases_repository import update_revoke_parking_release, \
    find_user_releases_for_revoke, find_release_for_confirm_revoke


async def get_user_releases_for_revoke(cur, db_user_id):
    today = date.today()
    results = await find_user_releases_for_revoke(cur, db_user_id, today)
    if not results:
        return None
    return [RevokeRelease(
        release_id=row[0],
        release_date=row[1],
        status=ParkingReleaseStatus(row[2]),
        spot_id=row[3],
    ) for row in results]

async def get_release_for_confirm_revoke(cur, release_id, db_user_id):
    result = await find_release_for_confirm_revoke(cur, db_user_id, release_id)
    if not result:
        return None
    return RevokeRelease(
        release_id=result[0],
        release_date=result[1],
        status=ParkingReleaseStatus(result[2]),
        spot_id=result[3],
    )

async def revoke_parking_release(cur, release_id, status):
    await update_revoke_parking_release(cur, release_id, status)