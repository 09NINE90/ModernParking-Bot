from app.repositories.admin_repository import AdminRepository


class AdminService:
    """Сервис для работы с запросами администратора"""

    def __init__(self, repository: AdminRepository):
        self.repository = repository

    def clear_tables(self):
        return self.repository.clear_tables()