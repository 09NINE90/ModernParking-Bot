from datetime import date

from app.data.models import ParkingTransfer
from app.repositories import StatisticsRepository


class StatisticsService:
    """Сервис для работы со статистикой"""

    def __init__(self, repository: StatisticsRepository):
        self.repository = repository

    def get_user_request_statistics(self, user_id):
        return self.repository.get_user_request_statistics(user_id)

    def get_user_release_statistics(self, user_id):
        return self.repository.get_user_release_statistics(user_id)

    def get_parking_transfers_by_date(self, rq_date: date):
        results = self.repository.get_parking_transfers_by_date(rq_date)
        if results:
            return [
                ParkingTransfer(
                    spot_id=row[0],
                    recipient_tg_id=row[1],
                    owner_tg_id=row[2]
                )
                for row in results
            ]
        return []

    def get_statistics_by_date_range(self, start_date: date, end_date: date):
        return self.repository.get_statistics_by_date_range(start_date, end_date)

    def get_parking_transfers_by_date_range(self, start_date: date, end_date: date):
        results = self.repository.get_parking_transfers_by_date_range(start_date, end_date)
        if results:
            return [
                ParkingTransfer(
                    spot_id=row[0],
                    recipient_tg_id=row[1],
                    owner_tg_id=row[2]
                )
                for row in results
            ]
        return []

    def get_all_statistics_by_all_time(self):
        return self.repository.get_all_statistics_by_all_time()
