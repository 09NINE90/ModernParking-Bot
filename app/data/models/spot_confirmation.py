from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid

from app.data.models.spot_confirmation_dto import SpotConfirmationDTO


@dataclass
class SpotConfirmation:
    """Модель для таблицы spot_confirmations"""
    id: str = None
    user_id: str = None
    release_id: Optional[str] = None
    request_id: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    is_active: bool = True

    def __post_init__(self):
        # Автоматическая генерация ID если не указан
        if self.id is None:
            self.id = str(uuid.uuid4())

        # Установка временных меток если не указаны
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    @classmethod
    def create_new(cls, db_user_id: str,  release_id: Optional[str] = None,
                   request_id: Optional[str] = None) -> 'SpotConfirmation':
        """Создает новое подтверждение места"""
        return cls(
            user_id=db_user_id,
            release_id=release_id,
            request_id=request_id
        )

    @classmethod
    def from_dto(cls, dto: 'SpotConfirmationDTO') -> 'SpotConfirmation':
        """Создает SpotConfirmation из DTO"""
        return cls.create_new(
            db_user_id=dto.db_user_id,
            release_id=dto.release_id,
            request_id=dto.request_id
        )

    def mark_as_inactive(self):
        """Помечает подтверждение как неактивное"""
        self.is_active = False
        self.updated_at = datetime.now()

    def update_timestamp(self):
        """Обновляет временную метку"""
        self.updated_at = datetime.now()
