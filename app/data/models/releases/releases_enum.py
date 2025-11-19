from enum import Enum


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