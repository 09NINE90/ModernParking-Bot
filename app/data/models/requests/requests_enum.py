from enum import Enum


class ParkingRequestStatus(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    CANCELED = "CANCELED"
    NOT_FOUND = "NOT_FOUND"
    WAITING_CONFIRMATION = "WAITING_CONFIRMATION"

    @property
    def display_name(self):
        """Возвращает человеко-читаемое название"""
        display_mapping = {
            'PENDING': 'Ожидание распределения мест',
            'ACCEPTED': 'Место получено',
            'CANCELED': 'Отказ от места',
            'NOT_FOUND': 'Место не найдено',
            'WAITING_CONFIRMATION': 'Ожидание подтверждения места'
        }
        return display_mapping.get(self.value, self.value)