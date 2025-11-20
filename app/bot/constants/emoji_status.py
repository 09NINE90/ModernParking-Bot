from app.bot.constants.log_types import LogNotification
from app.data.models.releases.parking_releases import ParkingReleaseStatus
from app.data.models.requests.parking_requests import ParkingRequestStatus


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

async def get_log_emoji(log_type: LogNotification):
    if log_type == LogNotification.ERROR:
        return '❌'
    elif log_type == LogNotification.WARN:
        return '⚠️'
    elif log_type == LogNotification.INFO:
        return 'ℹ️'
    return None