from dataclasses import dataclass
from datetime import date
from typing import Optional

from app.data.models.requests.requests_enum import ParkingRequestStatus


@dataclass
class RevokeRequest:
    request_id: str
    request_date: date
    status: ParkingRequestStatus
    spot_id: Optional[int]
    release_id: str = None