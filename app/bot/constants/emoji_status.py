from app.data.models.parking_releases import ParkingReleaseStatus
from app.data.models.parking_requests import ParkingRequestStatus


async def get_request_emoji_status(status):
    if status == ParkingRequestStatus.ACCEPTED:
        return "✅"
    else:
        return "⌛️"

async def get_release_emoji_status(status):
    if status == ParkingReleaseStatus.ACCEPTED:
        return "✅"
    else:
        return "⌛️"
