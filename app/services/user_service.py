import logging
from typing import Optional
from dataclasses import dataclass

from app.logs.log_builder import log_sync, LogType
from app.repositories.user_repository import UserRepository

from aiogram.enums import ChatMemberStatus
from app.bot import bot

logger = logging.getLogger(__name__)


@dataclass
class UserChatInfo:
    """Информация о пользователе в чате"""
    user_id: int
    chat_id: int
    is_member: bool
    is_admin: bool
    status: Optional[str] = None


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register_user(self, tg_user) -> bool:
        """
        Регистрирует пользователя

        Args:
            tg_user: Объект пользователя Telegram

        Returns:
            bool: True если успешно
        """
        try:
            # Создаем пользователя в БД
            created = self.repository.create_user(tg_user.id)
            return True

        except Exception as e:
            log_sync(log_message=f"Ошибка регистрации пользователя {tg_user.id}: {e}")
            return False

    @staticmethod
    async def is_user_in_chat(user_tg_id: int, group_id: int) -> bool:
        """
        Проверяет, является ли пользователь участником чата
        """
        try:
            member = await bot.get_chat_member(
                chat_id=group_id,
                user_id=user_tg_id
            )

            valid_statuses = [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.CREATOR,
            ]

            return member.status in valid_statuses

        except Exception as e:
            log_sync(log_message=f"UserService: Ошибка при проверке пользователя {user_tg_id}: {e}")
            return False

    def get_db_user_id_by_tg_id(self, user_tg_id):
        try:
            db_user_id = self.repository.get_db_user_id_by_tg_id(user_tg_id)

            if db_user_id:
                return db_user_id
            else:
                return None
        except Exception as e:
            log_sync(log_message=f"Не найден пользователь телеграмм ID {user_tg_id.id}: {e}")
            return None

    def update_user_rating_by_tg_id(self, tg_user_id: int, delta: int):
        return self.repository.update_user_rating_by_tg_id(tg_user_id, delta)

    def update_user_rating_by_user_id(self, db_user_id, delta: int, user_name: str = ''):
        return self.repository.update_user_rating_by_user_id(db_user_id, delta, user_name)

    def is_user_admin(self, tg_user_id: int) -> bool:
        return self.repository.is_user_admin(tg_user_id)
