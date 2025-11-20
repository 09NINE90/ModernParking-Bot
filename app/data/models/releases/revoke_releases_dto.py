from dataclasses import dataclass
from datetime import date
from typing import Optional

from app.data.models.releases.releases_enum import ParkingReleaseStatus


@dataclass
class RevokeRelease:
    release_id: str
    release_date: date
    status: ParkingReleaseStatus
    spot_id: Optional[int]
