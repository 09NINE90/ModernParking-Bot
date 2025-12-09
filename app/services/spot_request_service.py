from datetime import date

from app.data.models import RevokeRequest, ParkingRequest
from app.data.models.enumz.requests_statuses_enum import ParkingRequestStatus
from app.logs.log_builder import log_sync
from app.repositories.spot_request_repository import SpotRequestRepository


class SpotRequestService:
    """Сервис для работы с парковочными местами"""

    def __init__(self, repository: SpotRequestRepository):
        self.repository = repository

    def create_user_spot_request(
            self,
            db_user_id: str,
            request_date: date,
            is_auto_request: bool = False
    ) -> bool:
        """
        Создает запрос на парковочное место

        Returns:
            bool: True если успешно, False если ошибка или уже существует
        """
        try:

            return self.repository.insert_request_on_date(
                db_user_id=db_user_id,
                request_date=request_date,
                is_auto_request=is_auto_request
            )


        except Exception as e:
            log_sync(log_message=f"Ошибка создания освобождения места: {e}")
            return False

    def get_user_request_dates(self, user_id, from_date):
        return self.repository.get_user_request_dates(user_id, from_date)

    def get_spot_candidates(self, rq_date, limit: int):
        return self.repository.get_spot_candidates(rq_date, limit)

    def get_request_status_by_id(self, request_id):
        return self.repository.get_request_status_by_id(request_id)

    def update_parking_request_status(self, request_id, current_status: ParkingRequestStatus):
        return self.repository.update_parking_request_status(request_id, current_status)

    def get_user_requests_for_revoke(self, user_id, rq_date: date):
        results = self.repository.find_user_requests_for_revoke(user_id, rq_date)
        if results:
            return [RevokeRequest(
                request_id=row[0],
                request_date=row[1],
                status=ParkingRequestStatus(row[2]),
                spot_id=row[3],
            ) for row in results]

        return None

    def get_request_for_confirm_revoke(self, db_user_id, request_id):
        result = self.repository.find_request_for_confirm_revoke(db_user_id, request_id)
        if result:
            return RevokeRequest(
                request_id=result[0],
                request_date=result[1],
                status=ParkingRequestStatus(result[2]),
                spot_id=result[3],
                release_id=result[4]
            )
        return None

    def get_current_spots_request_by_user(self, user_id, rq_date: date):
        results = self.repository.get_current_spots_request_by_user(user_id, rq_date)
        if results:
            return [
                ParkingRequest(
                    status=row[0],
                    request_date=row[1],
                    spot_id=row[2]
                )
                for row in results
            ]
        return []

    def update_requests_statuses_to_not_found_by_date(self, rq_date: date):
        return self.repository.update_requests_statuses_to_not_found_by_date(rq_date)