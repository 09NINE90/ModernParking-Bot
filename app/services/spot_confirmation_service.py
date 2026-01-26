from app.data.models.dto.spot_confirmation_dto import SpotConfirmationDTO
from app.repositories.spot_confirmation_repository import SpotConfirmationRepository


class SpotConfirmationService:
    """Сервис для работы с парковочными местами"""

    def __init__(self, repository: SpotConfirmationRepository):
        self.repository = repository

    def create_spot_confirmation(self, spot_confirmation_data: SpotConfirmationDTO):
        return self.repository.insert_row_of_spot_confirmation(
            spot_confirmation_data.db_user_id,
            spot_confirmation_data.release_id,
            spot_confirmation_data.request_id
        )

    def get_spot_confirmation(self, user_id):
        return self.repository.find_spot_confirmations_by_user(user_id)

    def deactivate_spot_confirmations_by_user(self, user_id):
        return self.repository.deactivate_spot_confirmations_by_user(user_id)

    def deactivate_spot_confirmations_by_release(self, release_id):
        return self.repository.deactivate_spot_confirmations_by_release(release_id)

    def set_message_sent_id(self, spot_confirmation_id, message_sent_id):
        return self.repository.set_message_sent_id(spot_confirmation_id, message_sent_id)

    def get_message_sent_id(self, confirmation_id):
        return self.repository.get_message_sent_id(confirmation_id)

    def set_status(self, spot_confirmation_id, status):
        return self.repository.set_status(spot_confirmation_id, status)

    def get_waiting_confirmations_by_release_except_user(self, release_id, user_id):
        return self.repository.get_waiting_confirmations_by_release_except_user(release_id, user_id)

    def has_waiting_confirmations_for_release(self, release_id):
        return self.repository.has_waiting_confirmations_for_release(release_id)

    def get_all_waiting_confirmations_with_user(self):
        return self.repository.get_all_waiting_confirmations_with_user()

    def bulk_cancel_all_waiting(self):
        return self.repository.bulk_cancel_all_waiting()