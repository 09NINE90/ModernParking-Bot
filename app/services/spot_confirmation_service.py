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

    def set_message_sent_id(self, spot_confirmation_id, message_sent_id):
        return self.repository.set_message_sent_id(spot_confirmation_id, message_sent_id)

    def get_message_sent_id(self, user_id, release_id, request_id):
        return self.repository.get_message_sent_id(user_id, release_id, request_id)