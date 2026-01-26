from datetime import date

from app.data.models import ParkingTransfer, ParkingStatsPeriodDTO
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

    def get_parking_stats_by_period(self, period_type: str = "week", period_count: int = 1) -> list[
        ParkingStatsPeriodDTO]:
        rows = self.repository.get_parking_stats_by_period(period_type, period_count)
        dtos: list[ParkingStatsPeriodDTO] = []

        for r in rows:
            dtos.append(
                ParkingStatsPeriodDTO(
                    period_display=r["period_display"],
                    period_start=r["period_start"],
                    period_end=r["period_end"],
                    total_requests=r["total_requests"],
                    accepted_requests=r["accepted_requests"],
                    pending_requests=r["pending_requests"],
                    canceled_requests=r["canceled_requests"],
                    not_found_requests=r["not_found_requests"],
                    waiting_confirmation_requests=r["waiting_confirmation_requests"],
                    total_releases=r["total_releases"],
                    accepted_releases=r["accepted_releases"],
                    pending_releases=r["pending_releases"],
                    canceled_releases=r["canceled_releases"],
                    not_found_releases=r["not_found_releases"],
                    waiting_releases=r["waiting_releases"],
                    unique_requesters=r["unique_requesters"],
                    unique_releasers=r["unique_releasers"],
                    unique_recipients=r["unique_recipients"],
                    unique_spots_released=r["unique_spots_released"],
                    request_success_rate=r["request_success_rate"],
                    release_success_rate=r["release_success_rate"],
                    market_balance=r["market_balance"],
                )
            )

        return dtos
