from datetime import date
from typing import NamedTuple


class ParkingReminder(NamedTuple):
    spot_id: int
    user_tg_id: int
    db_user_id: str
    release_id: str
    release_date: date
    request_id: str