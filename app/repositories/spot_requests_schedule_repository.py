from contextlib import contextmanager

from app.config import settings
from app.logs.log_builder import log_sync


class SpotRequestsScheduleRepository:
    """Репозиторий для работы с расписаниями запросов на парковочные места"""

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

    def add_spot_requests_schedule(self, user_id, day_numbers) -> int | None | bool:
        """
            Добавляет расписание запросов на места для пользователя.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                    INSERT INTO {settings.DB_SCHEMA}.spot_requests_schedule (user_id, day_numbers)
                    VALUES (%s, %s)
                    ON CONFLICT (user_id, day_numbers) 
                    DO NOTHING
                    RETURNING id
                    """, (user_id, day_numbers))

                result = cur.fetchone()
                if result:
                    return result[0]
                else:
                    return None
        except Exception as e:
            log_sync(
                log_message=f"Ошибка добавления расписания запросов на места "
                            f"для пользователя {user_id}: {e}"
            )
            return False

    def get_spot_requests_schedule_by_user(self, user_id) -> list | None | bool:
        """
            Получает расписание запросов на места для указанного пользователя.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                    SELECT day_numbers FROM {settings.DB_SCHEMA}.spot_requests_schedule 
                    WHERE user_id = %s
                    """, (user_id,))

                results = cur.fetchall()
                if results:
                    return [row[0] for row in results]
                else:
                    return None
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения расписания запросов на места "
                            f"для пользователя {user_id}: {e}"
            )
            return False

    def get_spot_requests_schedule_by_user_with_id(self, user_id) -> list | None | bool:
        """
            Получает расписание запросов на места для указанного пользователя с ID записей.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                    SELECT id, day_numbers FROM {settings.DB_SCHEMA}.spot_requests_schedule 
                    WHERE user_id = %s
                    """, (user_id,))

                return cur.fetchall()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения расписания запросов на места с ID "
                            f"для пользователя {user_id}: {e}"
            )
            return False

    def get_spot_requests_schedule_by_id(self, schedule_id: str):
        """
            Получает полную запись расписания по его ID.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                    SELECT id, day_numbers FROM {settings.DB_SCHEMA}.spot_requests_schedule 
                    WHERE id = %s
                    """, (schedule_id,))

                return cur.fetchone()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения записи расписания по ID {schedule_id}: {e}"
            )
            return False

    def delete_spot_requests_schedule_by_id(self, schedule_id: str) -> bool:
        """
            Удаляет запись расписания по его ID.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                    DELETE FROM {settings.DB_SCHEMA}.spot_requests_schedule 
                    WHERE id = %s
                    """, (schedule_id,))

                return cur.rowcount > 0
        except Exception as e:
            log_sync(
                log_message=f"Ошибка удаления записи расписания по ID {schedule_id}: {e}"
            )
            return False

    def get_user_schedules_with_tg_id(self):
        """
            Получает все расписания пользователей с их TG ID.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                    SELECT u.tg_id,
                           JSON_AGG(
                                   JSON_BUILD_OBJECT(
                                           'id', srs.id,
                                           'day_numbers', srs.day_numbers
                                   )
                           ) as schedules
                    FROM {settings.DB_SCHEMA}.spot_requests_schedule srs
                             JOIN {settings.DB_SCHEMA}.users u ON u.user_id = srs.user_id
                    GROUP BY u.tg_id;
                    """)

                return cur.fetchall()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения расписаний пользователей с TG ID: {e}"
            )
            return False
