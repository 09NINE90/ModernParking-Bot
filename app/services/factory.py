from app.repositories import UserRepository, SpotReleaseRepository, SpotRequestRepository, SpotConfirmationRepository, \
    StatisticsRepository, ReminderSpotRepository
from app.services.reminder_spot_service import ReminderSpotService
from app.services.spot_confirmation_service import SpotConfirmationService
from app.services.spot_request_service import SpotRequestService
from app.services.statistics_service import StatisticsService
from app.services.user_service import UserService
from app.services.spot_release_service import SpotReleaseService


class ServiceFactory:
    """Фабрика для создания сервисов"""

    @staticmethod
    def create_user_service(connection) -> UserService:
        """Создает UserService с репозиторием"""
        repository = UserRepository(connection)
        return UserService(repository)

    @staticmethod
    def create_spot_release_service(connection) -> SpotReleaseService:
        """Создает SpotReleaseService с репозиторием"""
        repository = SpotReleaseRepository(connection)
        return SpotReleaseService(repository)

    @staticmethod
    def create_spot_request_service(connection) -> SpotRequestService:
        """Создает SpotRequestService с репозиторием"""
        repository = SpotRequestRepository(connection)
        return SpotRequestService(repository)

    @staticmethod
    def create_spot_confirmation_service(connection) -> SpotConfirmationService:
        repository = SpotConfirmationRepository(connection)
        return SpotConfirmationService(repository)

    @staticmethod
    def create_statistics_service(connection) -> StatisticsService:
        repository = StatisticsRepository(connection)
        return StatisticsService(repository)

    @staticmethod
    def create_reminder_spot_service(connection) -> ReminderSpotService:
        repository = ReminderSpotRepository(connection)
        return ReminderSpotService(repository)
