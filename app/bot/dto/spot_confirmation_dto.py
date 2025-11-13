from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class SpotConfirmationDTO:
    """DTO для передачи данных о подтверждении парковочного места"""
    db_user_id: str
    tg_user_id: int
    spot_number: int
    assignment_date: date
    release_id: Optional[str] = None
    request_id: Optional[str] = None

    def __post_init__(self):
        """Валидация данных после инициализации"""
        if not isinstance(self.tg_user_id, int) or self.tg_user_id <= 0:
            raise ValueError("tg_user_id должен быть положительным integer")
        if not isinstance(self.spot_number, int) or self.spot_number <= 0:
            raise ValueError("spot_number должен быть положительным integer")
        if not isinstance(self.assignment_date, date):
            raise ValueError("assignment_date должен быть datetime.date")