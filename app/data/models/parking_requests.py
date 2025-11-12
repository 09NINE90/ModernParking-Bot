import uuid
from datetime import datetime, date
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class ParkingRequestStatus(Enum):
    PENDING = "PENDING"
    ACCEPT = "ACCEPT"
    CANCELED = "CANCELED"
    NOT_FOUND = "NOT_FOUND"

# Модель для таблицы parking_requests
@dataclass
class ParkingRequest:
    id: uuid.UUID
    user_id: uuid.UUID
    request_date: date
    status: ParkingRequestStatus
    created_at: datetime
    processed_at: Optional[datetime] = None

    def __post_init__(self):
        if not isinstance(self.id, uuid.UUID):
            self.id = uuid.UUID(str(self.id))
        if not isinstance(self.user_id, uuid.UUID):
            self.user_id = uuid.UUID(str(self.user_id))
        if isinstance(self.status, str):
            self.status = ParkingRequestStatus(self.status)

    @classmethod
    def create_new(cls, user_id: uuid.UUID, request_date: date) -> 'ParkingRequest':
        return cls(
            id=uuid.uuid4(),
            user_id=user_id,
            request_date=request_date,
            status=ParkingRequestStatus.PENDING,
            created_at=datetime.now(),
            processed_at=None
        )

    def mark_as_accepted(self):
        self.status = ParkingRequestStatus.ACCEPT
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