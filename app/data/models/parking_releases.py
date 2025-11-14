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

    @property
    def display_name(self):
        """Возвращает человеко-читаемое название"""
        display_mapping = {
            'PENDING': 'Ожидание распределения мест',
            'ACCEPTED': 'Место отдано',
            'CANCELED': 'Отмена освобождения места',
            'NOT_FOUND': 'Место не отдано',
            'WAITING': 'Ожидание подтверждения места'
        }
        return display_mapping.get(self.value, self.value)

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
