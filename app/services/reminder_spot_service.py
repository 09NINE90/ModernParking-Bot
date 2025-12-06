from app.data.models import ParkingReminder
from app.repositories import ReminderSpotRepository


class ReminderSpotService:
    """Сервис для работы с парковочными местами"""

    def __init__(self, repository: ReminderSpotRepository):
        self.repository = repository

    def create_reminder_spot_confirmations(self, user_id, release_id, request_id):
        result = self.repository.insert_row_of_reminder_spot_confirmations(
            user_id=user_id,
            release_id=release_id,
            request_id=request_id
        )
        if not result:
            return None

        return result[0]

    def get_reminder_spot_confirmations_by_user(self, user_id):
        result = self.repository.find_reminder_spot_confirmations_by_user(
            user_id=user_id
        )
        if result:
            return ParkingReminder(
                spot_id=result[2],
                user_tg_id=result[1],
                db_user_id=result[0],
                release_id=result[4],
                release_date=result[3],
                request_id=result[5]
            )
        return None

    def deactivate_reminder_spot_confirmations_by_user(self, user_id):
        return self.repository.deactivate_reminder_spot_confirmations_by_user(
            user_id=user_id
        )

    def set_message_sent_id(self, reminder_id, message_sent_id):
        return self.repository.set_message_sent_id(reminder_id, message_sent_id)

    def get_message_sent_id(self, user_id, release_id, request_id):
        return self.repository.get_message_sent_id(user_id, release_id, request_id)
