import uuid

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Optional

class ParkingReleaseStatus(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    CANCELED = "CANCELED"
    NOT_FOUND = "NOT_FOUND"
    WAITING = "WAITING"

# Модель для таблицы parking_releases
@dataclass
class ParkingRelease:
    id: uuid.UUID
    user_id: uuid.UUID
    spot_id: int
    release_date: date
    created_at: datetime
    user_id_took: Optional[uuid.UUID] = None

    def __post_init__(self):
        if not isinstance(self.id, uuid.UUID):
            self.id = uuid.UUID(str(self.id))
        if self.user_id_took and not isinstance(self.user_id_took, uuid.UUID):
            self.user_id_took = uuid.UUID(str(self.user_id_took))
        if not isinstance(self.user_id, uuid.UUID):
            self.user_id = uuid.UUID(str(self.user_id))

    @classmethod
    def create_new(cls, user_id: uuid.UUID, spot_id: int, release_date: date) -> 'ParkingRelease':
        return cls(
            id=uuid.uuid4(),
            user_id=user_id,
            spot_id=spot_id,
            release_date=release_date,
            created_at=datetime.now(),
            user_id_took=None
        )
