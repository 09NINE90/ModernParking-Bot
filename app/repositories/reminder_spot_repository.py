from contextlib import contextmanager

from app.config import settings
from app.logs.log_builder import log_sync


class ReminderSpotRepository:
    """
        Репозиторий для работы с подтверждениями парковочных мест
        при напоминании пользователю
    """

    def __init__(self, connection):
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

    def insert_row_of_reminder_spot_confirmations(self, user_id, release_id, request_id):
        """
            Добавление записи с напоминанием о занятом месте
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                        INSERT INTO {settings.DB_SCHEMA}.reminder_spot_confirmations 
                        (user_id, release_id, request_id)
                        VALUES (%s, %s, %s)
                        RETURNING id
                        """, (user_id, release_id, request_id,))
                return cur.fetchone()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка при добавлении записи с напоминанием о занятом месте: {e}"
            )

    def find_reminder_spot_confirmations_by_user(self, user_id):
        """
            Поиск активного напоминания о занятом месте для пользователя
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                        SELECT u.user_id, u.tg_id, prl.spot_id, prl.release_date, sc.release_id, sc.request_id
                        FROM {settings.DB_SCHEMA}.reminder_spot_confirmations sc
                                 JOIN {settings.DB_SCHEMA}.users u ON u.user_id = sc.user_id
                                 JOIN {settings.DB_SCHEMA}.parking_releases prl ON prl.id = sc.release_id
                        WHERE sc.user_id = %s
                          AND sc.is_active = TRUE
                        ORDER BY sc.created_at DESC
                        LIMIT 1
                        """, (user_id,))

                return cur.fetchone()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка при поиске напоминания о занятом месте для пользователя: {e}"
            )
            return None

    def deactivate_reminder_spot_confirmations_by_user(self, user_id):
        """
            Деактивация активных напоминаний о занятом месте для пользователя
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                        UPDATE {settings.DB_SCHEMA}.reminder_spot_confirmations
                        SET is_active  = FALSE,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id IN (SELECT user_id
                                          FROM {settings.DB_SCHEMA}.users
                                          WHERE user_id = %s)
                          AND is_active = TRUE
                        """, (user_id,))
        except Exception as e:
            log_sync(
                log_message=f"Ошибка при деактивации напоминаний о занятом месте для пользователя: {e}"
            )

    def set_message_sent_id(self, reminder_id, message_sent_id):
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                            UPDATE {settings.DB_SCHEMA}.reminder_spot_confirmations
                            SET message_sent_id = %s
                            WHERE id = %s
                            """,
                            (message_sent_id, reminder_id,))
        except Exception as e:
            log_sync(
                log_message=f"Ошибка добавления ID сообщения для подтверждения: {e}"
            )
            return None

    def get_message_sent_id(self, user_id, release_id, request_id):
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                                SELECT message_sent_id 
                                FROM {settings.DB_SCHEMA}.reminder_spot_confirmations 
                                WHERE user_id = %s 
                                    AND release_id = %s 
                                    AND request_id = %s
                                """,
                            (user_id, release_id, request_id,))

                result = cur.fetchone()

                if result and result[0] is not None:
                    return result[0]
                return None
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения ID сообщения для подтверждения user_id: {user_id}, request_id: {request_id}: {e}"
            )
            return None
