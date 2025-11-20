import uuid
from datetime import datetime, date
from typing import Optional
from dataclasses import dataclass

from app.data.models.requests.requests_enum import ParkingRequestStatus


# Модель для таблицы parking_requests
@dataclass
class ParkingRequest:
    id: str = None
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

    def mark_as_accepted(self):
        self.status = ParkingRequestStatus.ACCEPTED
        self.processed_at = datetime.now()

    def mark_as_canceled(self):
        self.status = ParkingRequestStatus.CANCELED
        self.processed_at = datetime.now()

    def mark_as_not_found(self):
        self.status = ParkingRequestStatus.NOT_FOUND
        self.processed_at = datetime.now()

    def is_pending(self) -> bool:
        return self.status == ParkingRequestStatus.PENDING

    def is_processed(self) -> bool:
        return self.processed_at is not None
