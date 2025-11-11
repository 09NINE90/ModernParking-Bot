from datetime import datetime, date
from typing import List, Optional
from enum import Enum

class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class ParkingRequestStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.status = UserStatus.ACTIVE
        self.rating = 0
        self.created_at = datetime.now()

class ParkingSpot:
    def __init__(self, spot_id: str):
        self.spot_id = spot_id
        self.is_active = True

class ParkingRelease:
    def __init__(self, user_id: int, spot_id: str, release_date: date):
        self.user_id = user_id
        self.spot_id = spot_id
        self.release_date = release_date
        self.created_at = datetime.now()
        self.is_processed = False

class ParkingRequest:
    def __init__(self, user_id: int, request_date: date):
        self.user_id = user_id
        self.request_date = request_date
        self.status = ParkingRequestStatus.PENDING
        self.created_at = datetime.now()
        self.processed_at = None


