import logging
import psycopg2

from typing import Optional, Dict, Any
from contextlib import contextmanager
from psycopg2.extras import RealDictCursor

from app.config import settings
from app.logs.log_builder import log_sync, LogType

logger = logging.getLogger(__name__)


class UserRepository:
    """Репозиторий для работы с пользователями в БД"""

    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    @contextmanager
    def _get_cursor(self, cursor_factory=None):
        """Контекстный менеджер для работы с курсором"""
        cursor = self.connection.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def create_user(self, tg_id: int) -> bool:
        """
        Создает нового пользователя

        Returns:
            bool: True если создан, False если ошибка или уже существует
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO {settings.DB_SCHEMA}.users 
                    (user_id, tg_id, created_at)
                    VALUES (gen_random_uuid(), %s, NOW())
                    ON CONFLICT (tg_id) DO NOTHING
                    RETURNING user_id
                    """,
                    (tg_id,)
                )

                result = cur.fetchone()
                if result:
                    log_sync(log_type=LogType.INFO,
                             log_message=f"Пользователь зарегистрирован: {tg_id}"
                             )
                    return True
                else:
                    log_sync(log_type=LogType.INFO,
                             log_message=f"Пользователь уже существует: {tg_id}",
                             is_sending_log=False
                             )
                    return True

        except Exception as e:
            logger.error(f"Ошибка создания пользователя {tg_id}: {e}")
            return False

    def get_db_user_id_by_tg_id(self, tg_id: int) -> str | None:
        """Получает пользователя по Telegram ID"""
        try:
            with self._get_cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT user_id FROM {settings.DB_SCHEMA}.users 
                    WHERE tg_id = %s
                    """,
                    (tg_id,)
                )
                result = cur.fetchone()
                if result:
                    return result.get('user_id')
                else:
                    return None
        except Exception as e:
            log_sync(log_message=f"Ошибка получения пользователя {tg_id}: {e}")
            return None

    def get_user_by_tg_id(self, tg_id: int) -> Optional[Dict[str, Any]]:
        """Получает пользователя по Telegram ID"""
        try:
            with self._get_cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT * FROM {settings.DB_SCHEMA}.users 
                    WHERE tg_id = %s
                    """,
                    (tg_id,)
                )
                return cur.fetchone()
        except Exception as e:
            log_sync(log_message=f"Ошибка получения пользователя {tg_id}: {e}")
            return None

    def user_exists(self, tg_id: int) -> bool:
        """Проверяет существование пользователя"""
        try:
            with self._get_cursor() as cur:
                cur.execute(
                    f"""
                    SELECT 1 FROM {settings.DB_SCHEMA}.users 
                    WHERE tg_id = %s
                    """,
                    (tg_id,)
                )
                return cur.fetchone() is not None
        except Exception as e:
            log_sync(log_message=f"Ошибка проверки пользователя {tg_id}: {e}")
            return False

    def update_user_rating_by_tg_id(self, tg_id: int, delta: int) -> bool:
        """Обновляет рейтинг пользователя"""
        try:
            with self._get_cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE {settings.DB_SCHEMA}.users 
                    SET rating = rating + %s
                    WHERE tg_id = %s
                    RETURNING rating
                    """,
                    (delta, tg_id)
                )
                result = cur.fetchone()
                if result:
                    log_sync(
                        log_type=LogType.INFO,
                        log_message=f"Рейтинг пользователя {tg_id} изменен на {delta}"
                    )
                    return True
                return False
        except Exception as e:
            log_sync(log_message=f"Ошибка обновления рейтинга пользователя {tg_id}: {e}")
            return False

    def update_user_rating_by_user_id(self, db_user_id, delta: int) -> bool:
        """Обновляет рейтинг пользователя"""
        try:
            with self._get_cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE {settings.DB_SCHEMA}.users 
                    SET rating = rating + %s
                    WHERE user_id = %s
                    RETURNING rating
                    """,
                    (delta, db_user_id)
                )
                result = cur.fetchone()
                if result:
                    log_sync(
                        log_type=LogType.INFO,
                        log_message=f"Рейтинг пользователя {db_user_id} изменен на {delta} "
                                    f"и равен {result[0]}"
                    )
                    return True
                return False
        except Exception as e:
            log_sync(log_message=f"Ошибка обновления рейтинга пользователя {db_user_id}: {e}")
            return False

    def set_user_role(self, tg_id: int, role: str) -> bool:
        """Устанавливает роль пользователя"""
        try:
            with self._get_cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE {settings.DB_SCHEMA}.users 
                    SET roles = %s
                    WHERE tg_id = %s
                    RETURNING roles
                    """,
                    (role, tg_id)
                )
                result = cur.fetchone()
                if result:
                    log_sync(
                        log_type=LogType.INFO,
                        log_message=f"Роль пользователя {tg_id} изменена на {role}"
                    )
                    return True
                return False
        except Exception as e:
            log_sync(log_message=f"Ошибка изменения роли пользователя {tg_id}: {e}")
            return False

    def get_user_rating(self, tg_id: int) -> Optional[int]:
        """Получает рейтинг пользователя"""
        user = self.get_user_by_tg_id(tg_id)
        return user.get('rating') if user else None

    def is_user_admin(self, tg_id: int) -> bool:
        """Проверяет, является ли пользователь администратором"""
        user = self.get_user_by_tg_id(tg_id)
        return user and user.get('roles') == 'ADMIN'

    def update_user_status(self, tg_id: int, status: bool) -> bool:
        """Обновляет статус пользователя (активен/неактивен)"""
        try:
            with self._get_cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE {settings.DB_SCHEMA}.users
                    SET status = %s
                    WHERE tg_id = %s
                    RETURNING status
                    """,
                    (status, tg_id)
                )
                result = cur.fetchone()
                if result:
                    log_sync(
                        log_type=LogType.INFO,
                        log_message=f"Статус пользователя {tg_id} изменен на {status}"
                    )
                    return True
                return False
        except Exception as e:
            log_sync(log_message=f"Ошибка изменения статуса пользователя {tg_id}: {e}")
            return False

    def get_all_users(self, active_only: bool = True) -> list:
        """Получает всех пользователей"""
        try:
            with self._get_cursor(cursor_factory=RealDictCursor) as cur:
                if active_only:
                    cur.execute(
                        f"""
                        SELECT *
                        FROM {settings.DB_SCHEMA}.users
                        WHERE status = TRUE
                        ORDER BY rating DESC, created_at
                        """
                    )
                else:
                    cur.execute(
                        f"""
                        SELECT *
                        FROM {settings.DB_SCHEMA}.users
                        ORDER BY rating DESC, created_at
                        """
                    )
                return cur.fetchall()
        except Exception as e:
            log_sync(log_message=f"Ошибка получения пользователей: {e}")
            return []
