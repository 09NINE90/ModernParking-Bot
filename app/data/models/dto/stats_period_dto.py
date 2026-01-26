from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class ParkingStatsPeriodDTO:
    period_display: str
    period_start: datetime
    period_end: datetime

    total_requests: int
    accepted_requests: int
    pending_requests: int
    canceled_requests: int
    not_found_requests: int
    waiting_confirmation_requests: int

    total_releases: int
    accepted_releases: int
    pending_releases: int
    canceled_releases: int
    not_found_releases: int
    waiting_releases: int

    unique_requesters: int
    unique_releasers: int
    unique_recipients: int
    unique_spots_released: int

    request_success_rate: Optional[Decimal]
    release_success_rate: Optional[Decimal]

    market_balance: str
