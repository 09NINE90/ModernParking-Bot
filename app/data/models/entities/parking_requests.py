import uuid
from datetime import datetime, date
from typing import Optional
from dataclasses import dataclass

from app.data.models.enumz.requests_statuses_enum import ParkingRequestStatus


# Модель для таблицы parking_requests
@dataclass
class ParkingRequest:
    id: str = None
    spot_id: int = None
    user_id: str = None
    request_date: date = None
    status: ParkingRequestStatus = None
    created_at: datetime = None
    processed_at: Optional[datetime] = None

    def __post_init__(self):
        if isinstance(self.status, str):
            self.status = ParkingRequestStatus(self.status)

    @classmethod
    def create_new(cls, user_id: str, request_date: date) -> 'ParkingRequest':
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            request_date=request_date,
            status=ParkingRequestStatus.PENDING,
            created_at=datetime.now(),
            processed_at=None
        )
