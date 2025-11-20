import uuid

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from app.data.models.releases.releases_enum import ParkingReleaseStatus


# Модель для таблицы parking_releases
@dataclass
class ParkingRelease:
    id: str = None
    user_id: str = None
    spot_id: int = None
    release_date: date = None
    status: ParkingReleaseStatus = None
    created_at: datetime = None
    user_id_took: Optional[uuid.UUID] = None

    def __post_init__(self):
        if isinstance(self.status, str):
            self.status = ParkingReleaseStatus(self.status)

    @classmethod
    def create_new(cls, user_id: str, spot_id: int, release_date: date) -> 'ParkingRelease':
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            spot_id=spot_id,
            release_date=release_date,
            created_at=datetime.now(),
            user_id_took=None
        )
