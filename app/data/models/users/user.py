from dataclasses import dataclass
from datetime import datetime

from app.data.models.users.user_roles import UserRoles


@dataclass
class User:
    """Сущность пользователя"""
    user_id: str = None
    tg_id: int = None
    status: bool = True
    rating: int = 0
    role: UserRoles = UserRoles.USER
    created_at: datetime = None

    def __post_init__(self):
        """Валидация данных после инициализации"""
        if not isinstance(self.tg_id, int) or self.tg_id <= 0:
            raise ValueError("tg_user_id должен быть положительным integer")
        if not isinstance(self.rating, int) or self.rating < 0:
            raise ValueError("rating должен быть неотрицательным integer")
        if isinstance(self.role, str):
            self.role = UserRoles(self.role)