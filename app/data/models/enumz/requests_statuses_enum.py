from enum import Enum

from app.utils.emoji_util import waiting_emoji, sber_accept_emoji, canceled_emoji, not_found_emoji


class ParkingRequestStatus(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    CANCELED = "CANCELED"
    NOT_FOUND = "NOT_FOUND"
    WAITING_CONFIRMATION = "WAITING_CONFIRMATION"

    @property
    def display_name(self) -> str:
        """Возвращает человеко-читаемое название"""
        display_mapping = {
            'PENDING': 'Ожидание распределения мест',
            'ACCEPTED': 'Место получено',
            'CANCELED': 'Отказ от места',
            'NOT_FOUND': 'Место не найдено',
            'WAITING_CONFIRMATION': 'Ожидание подтверждения места'
        }
        return display_mapping.get(self.value, self.value)

    @property
    def emoji(self) -> str:
        display_mapping = {
            'PENDING': f'{waiting_emoji}',
            'ACCEPTED': f'{sber_accept_emoji}',
            'CANCELED': f'{canceled_emoji}',
            'NOT_FOUND': f'{not_found_emoji}',
            'WAITING_CONFIRMATION': f'{waiting_emoji}',
        }
        return display_mapping.get(self.value, self.value)
