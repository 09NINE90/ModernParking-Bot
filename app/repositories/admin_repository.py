from contextlib import contextmanager

from app.config import settings
from app.logs.log_builder import log_sync


class AdminRepository:
    """
        Репозиторий для администратора
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

    def clear_tables(self):
        """
        Очищает доменные таблицы и сбрасывает рейтинг.

        Returns:
            dict: количество удалённых строк по таблицам:
                  {
                      "spot_confirmations": int,
                      "reminder_spot_confirmations": int,
                      "parking_requests": int,
                      "parking_releases": int,
                  }
        """
        stats = {
            "spot_confirmations": 0,
            "reminder_spot_confirmations": 0,
            "parking_requests": 0,
            "parking_releases": 0,
        }

        try:
            with self._get_cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM {settings.DB_SCHEMA}.spot_confirmations")
                stats["spot_confirmations"] = cur.fetchone()[0]

                cur.execute(f"SELECT COUNT(*) FROM {settings.DB_SCHEMA}.reminder_spot_confirmations")
                stats["reminder_spot_confirmations"] = cur.fetchone()[0]

                cur.execute(f"SELECT COUNT(*) FROM {settings.DB_SCHEMA}.parking_requests")
                stats["parking_requests"] = cur.fetchone()[0]

                cur.execute(f"SELECT COUNT(*) FROM {settings.DB_SCHEMA}.parking_releases")
                stats["parking_releases"] = cur.fetchone()[0]

                cur.execute(f"""
                    TRUNCATE 
                        {settings.DB_SCHEMA}.spot_confirmations,
                        {settings.DB_SCHEMA}.reminder_spot_confirmations,
                        {settings.DB_SCHEMA}.parking_requests,
                        {settings.DB_SCHEMA}.parking_releases
                    RESTART IDENTITY CASCADE;
                """)

                cur.execute(f"""
                    UPDATE {settings.DB_SCHEMA}.users 
                    SET rating = 0;
                """)

            return stats
        except Exception as e:
            log_sync(log_message=f"Ошибка очистки таблиц: {e}")
            return None
