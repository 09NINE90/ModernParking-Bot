from enum import Enum

from app.utils.emoji_util import waiting_emoji, sber_accept_emoji, canceled_emoji, not_found_emoji


class ParkingReleaseStatus(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    CANCELED = "CANCELED"
    NOT_FOUND = "NOT_FOUND"
    WAITING = "WAITING"

    @property
    def display_name(self):
        """Возвращает человеко-читаемое название"""
        display_mapping = {
            'PENDING': 'Ожидание распределения мест',
            'ACCEPTED': 'Место отдано',
            'CANCELED': 'Отмена освобождения места',
            'NOT_FOUND': 'Место не отдано',
            'WAITING': 'Ожидание подтверждения места'
        }
        return display_mapping.get(self.value, self.value)

    @property
    def emoji(self) -> str:
        display_mapping = {
            'PENDING': f'{waiting_emoji}',
            'ACCEPTED': f'{sber_accept_emoji}',
            'CANCELED': f'{canceled_emoji}',
            'NOT_FOUND': f'{not_found_emoji}',
            'WAITING': f'{waiting_emoji}'
        }
        return display_mapping.get(self.value, self.value)
