from datetime import date

from app.data.models import RevokeRelease, ParkingRelease, ParkingReminder
from app.data.models.enumz.releases_statuses_enum import ParkingReleaseStatus
from app.logs.log_builder import log_sync
from app.repositories.spot_release_repository import SpotReleaseRepository


class SpotReleaseService:
    """Сервис для работы с парковочными местами"""

    def __init__(self, repository: SpotReleaseRepository):
        self.repository = repository

    def is_valid_spot_number(self, spot_number: int) -> bool:
        """Проверяет валидность номера места"""
        try:
            spot_num = int(spot_number)
            spot = self.repository.get_active_spot_by_id(spot_num)
            return spot is not None
        except (ValueError, Exception) as e:
            log_sync(log_message=f"Ошибка проверки места {spot_number}: {e}")
            return False

    def create_spot_release(
            self,
            db_user_id: str,
            spot_number: int,
            release_date: date
    ) -> bool:
        """
        Создает освобождение места

        Returns:
            bool: True если успешно, False если ошибка или уже существует
        """
        try:

            return self.repository.insert_spot_on_date(
                db_user_id, spot_number, release_date
            )

        except Exception as e:
            log_sync(log_message=f"Ошибка создания освобождения места: {e}")
            return False

    def get_user_releases_dates(self, user_id, spot_id, from_date):
        return self.repository.get_user_releases_dates(user_id, spot_id, from_date)

    def get_user_spot_by_date(self, request_date, db_user_id):
        return self.repository.get_user_spot_by_date(request_date, db_user_id)

    def get_dates_with_availability(self):
        return self.repository.get_dates_with_availability()

    def get_free_spots_by_date(self, rq_date):
        return self.repository.get_free_spots_by_date(rq_date)

    def is_spot_still_available(self, release_id):
        return self.repository.is_spot_still_available(release_id)

    def update_parking_releases(self, user_id, release_id, current_status: ParkingReleaseStatus):
        return self.repository.update_parking_releases(user_id, release_id, current_status)

    def update_release_status(self, release_id, current_status: ParkingReleaseStatus):
        return self.repository.update_release_status(release_id, current_status)

    def accept_spot_if_free(self, release_id, user_id):
        return self.repository.accept_spot_if_free(release_id, user_id)

    def get_release_owner(self, release_id):
        return self.repository.get_release_owner(release_id)

    def get_release_status_by_id(self, release_id):
        return self.repository.get_release_status_by_id(release_id)

    def update_parking_release_set_free(self, release_id, current_status: ParkingReleaseStatus):
        return self.repository.update_parking_release_set_free(release_id, current_status)

    def get_user_releases_for_revoke(self, db_user_id, rq_date: date):
        results = self.repository.find_user_releases_for_revoke(db_user_id, rq_date)
        if results:
            return [RevokeRelease(
                release_id=row[0],
                release_date=row[1],
                status=ParkingReleaseStatus(row[2]),
                spot_id=row[3],
            ) for row in results]

        return None

    def get_release_for_confirm_revoke(self, db_user_id, release_id):
        result = self.repository.find_release_for_confirm_revoke(db_user_id, release_id)
        if result:
            return RevokeRelease(
                release_id=result[0],
                release_date=result[1],
                status=ParkingReleaseStatus(result[2]),
                spot_id=result[3],
            )

        return None

    def get_current_spots_releases_by_user(self, user_id, rq_date: date):
        results = self.repository.get_current_spots_releases_by_user(user_id, rq_date)
        if results:
            return [
                ParkingRelease(
                    spot_id=row[0],
                    status=row[1],
                    release_date=row[2]
                )
                for row in results
            ]
        return []

    def get_free_parking_releases_by_date(self, rq_date: date):
        return self.repository.get_free_parking_releases_by_date(rq_date)

    def get_count_waiting_releases_by_date(self, rq_date: date):
        return self.repository.get_count_waiting_releases_by_date(rq_date)

    def get_accepted_spot_by_date(self, rq_date: date):
        results = self.repository.get_accepted_spot_by_date(rq_date)

        if results:
            return [
                ParkingReminder(
                    spot_id=row[0],
                    user_tg_id=row[1],
                    db_user_id=row[2],
                    release_id=row[3],
                    release_date=row[4],
                    request_id=row[5]
                )
                for row in results
            ]

        return []

    def update_releases_statuses_to_not_found_by_date(self, rq_date: date):
        return self.repository.update_releases_statuses_to_not_found_by_date(rq_date)

    def mark_releases_not_found_if_only_cancelled(self, confirmations):
        return self.repository.mark_releases_not_found_if_only_cancelled(confirmations)