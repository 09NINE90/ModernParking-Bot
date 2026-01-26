from contextlib import contextmanager

from app.config import settings
from app.data.models import ConfirmationStatus
from app.logs.log_builder import log_sync


class SpotConfirmationRepository:
    """Репозиторий для работы с подтверждениями парковочных мест"""

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

    def insert_row_of_spot_confirmation(self, user_id, release_id, request_id):
        """
            Создает новую запись о подтверждении парковочного места.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                        INSERT INTO {settings.DB_SCHEMA}.spot_confirmations (id, user_id, release_id, request_id)
                        VALUES (gen_random_uuid(), %s, %s, %s)
                        RETURNING id
                        """, (user_id, release_id, request_id,))

                result = cur.fetchone()
                if result:
                    return result[0]
                else:
                    return None
        except Exception as e:
            log_sync(
                log_message=f"Ошибка создания новой записи о подтверждении парковочного места: {e}"
            )
            return None

    def find_spot_confirmations_by_user(self, user_id):
        """
            Находит последнее подтверждение парковочного места для пользователя
            в статусе WAITING (ожидает ответа).
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                    SELECT sc.id,                 
                           u.user_id,
                           u.tg_id,
                           prl.spot_id,
                           prl.release_date,
                           sc.release_id,
                           sc.request_id,
                           sc.message_sent_id
                    FROM {settings.DB_SCHEMA}.spot_confirmations sc
                    JOIN {settings.DB_SCHEMA}.users u ON u.user_id = sc.user_id
                    JOIN {settings.DB_SCHEMA}.parking_releases prl ON prl.id = sc.release_id
                    WHERE sc.user_id = %s
                      AND sc.status = 'WAITING'
                    ORDER BY sc.created_at DESC
                    LIMIT 1
                """, (user_id,))

                return cur.fetchone()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения ожидающего подтверждения пользователя: {e}"
            )
            return None

    def deactivate_spot_confirmations_by_user(self, user_id):
        """
            Деактивирует все активные подтверждения парковочных мест пользователя.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                        UPDATE {settings.DB_SCHEMA}.spot_confirmations
                        SET is_active  = FALSE,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id IN (SELECT user_id
                                          FROM {settings.DB_SCHEMA}.users
                                          WHERE user_id = %s)
                          AND is_active = TRUE
                        """, (user_id,))
        except Exception as e:
            log_sync(
                log_message=f"Ошибка деактивации подтверждения пользователя: {e}"
            )
            return None

    def deactivate_spot_confirmations_by_release(self, release_id: int):
        """
            Деактивирует все активные подтверждения по конкретному релизу (месту).
            Вызывается, когда кто-то уже занял это место.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                    UPDATE {settings.DB_SCHEMA}.spot_confirmations
                    SET is_active  = FALSE,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE release_id = %s
                      AND is_active = TRUE
                """, (release_id,))
        except Exception as e:
            log_sync(
                log_message=f"Ошибка деактивации подтверждений по релизу: {e}"
            )
            return None

    def set_message_sent_id(self, spot_confirmation_id, message_sent_id):
        """
           Сохраняет ID отправленного Telegram-сообщения для указанного подтверждения.
       """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                            UPDATE {settings.DB_SCHEMA}.spot_confirmations
                            SET message_sent_id = %s
                            WHERE id = %s
                            """,
                            (message_sent_id, spot_confirmation_id,))
        except Exception as e:
            log_sync(
                log_message=f"Ошибка добавления ID сообщения для подтверждения: {e}"
            )
            return None

    def get_message_sent_id(self, confirmation_id):
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                                SELECT message_sent_id 
                                FROM {settings.DB_SCHEMA}.spot_confirmations 
                                WHERE id = %s
                                """,
                            (confirmation_id,))

                result = cur.fetchone()

                if result and result[0] is not None:
                    return result[0]
                return None
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения ID сообщения для подтверждения confirmation_id: {confirmation_id}: {e}"
            )
            return None

    def set_status(self, spot_confirmation_id, status: ConfirmationStatus):
        """
            Изменение статуса подтверждения по ID
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                            UPDATE {settings.DB_SCHEMA}.spot_confirmations
                            SET status  = %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = %s
                        """, (status.name, spot_confirmation_id,))

        except Exception as e:
            log_sync(
                log_message=f"Ошибка обновления статуса подтверждения на {status.name}: {e}"
            )
            return None

    def get_waiting_confirmations_by_release_except_user(self, release_id, user_id):
        """
            Возвращает все подтверждения со статусом WAITING
            для указанного релиза, кроме подтверждения текущего пользователя.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                    SELECT sc.id,
                           sc.user_id,
                           sc.request_id,
                           sc.message_sent_id,
                           u.tg_id
                    FROM {settings.DB_SCHEMA}.spot_confirmations sc
                    JOIN {settings.DB_SCHEMA}.users u ON sc.user_id = u.user_id
                    WHERE sc.release_id = %s
                      AND sc.status = 'WAITING'
                      AND sc.user_id <> %s
                """, (release_id, user_id))

                return cur.fetchall()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения подтверждений по релизу (исключая пользователя): {e}"
            )
            return []

    def has_waiting_confirmations_for_release(self, release_id) -> bool:
        """
            Проверяет, остались ли подтверждения со статусом WAITING для указанного релиза.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                    SELECT COUNT(*)
                    FROM {settings.DB_SCHEMA}.spot_confirmations
                    WHERE release_id = %s
                      AND status = 'WAITING'
                """, (release_id,))
                count, = cur.fetchone()
                return count > 0
        except Exception as e:
            log_sync(log_message=f"Ошибка проверки WAITING-подтверждений по релизу: {e}")
            return False

    def get_all_waiting_confirmations_with_user(self):
        """
            Возвращает все подтверждения со статусом WAITING вместе с данными пользователей
            для массовой обработки истечения времени ожидания.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                            SELECT sc.id,
                                   sc.user_id,
                                   sc.request_id,
                                   sc.release_id,
                                   sc.message_sent_id,
                                   u.tg_id
                            FROM {settings.DB_SCHEMA}.spot_confirmations sc
                                JOIN {settings.DB_SCHEMA}.parking_requests pr ON pr.id = sc.request_id
                                JOIN {settings.DB_SCHEMA}.parking_releases prl ON prl.id = sc.release_id
                                JOIN {settings.DB_SCHEMA}.users u ON u.user_id = sc.user_id
                            WHERE sc.status = 'WAITING';
                            """)

                return cur.fetchall()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения ожидающих подтверждений: {e}"
            )
            return []

    def bulk_cancel_all_waiting(self):
        """
            Массово переводит все подтверждения со статусом WAITING в CANCELLED.
            Вызывается при истечении времени ожидания (ежедневно в 18:00).
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                            UPDATE {settings.DB_SCHEMA}.spot_confirmations
                            SET status = 'CANCELLED',
                                updated_at = CURRENT_TIMESTAMP
                            WHERE status = 'WAITING';
                            """)
        except Exception as e:
            log_sync(
                log_message=f"Ошибка обновления статусов ожидающих подтверждений на отмененные: {e}"
            )
