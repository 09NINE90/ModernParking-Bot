from contextlib import contextmanager
from datetime import date

from app.config import settings
from app.logs.log_builder import log_sync


class StatisticsRepository:
    """Репозиторий для работы со статистикой"""

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

    def get_user_request_statistics(self, user_id):
        """
            Получение статистики по запросам пользователя
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                       SELECT 
                           COUNT(*) as total_user_requests,
                           COUNT(*) FILTER (WHERE status = 'ACCEPTED') as accepted_spots_count,
                           COUNT(*) FILTER (WHERE status = 'CANCELED') as canceled_spots_count,
                           COUNT(*) FILTER (WHERE status = 'NOT_FOUND') as not_found_spots_count
                       FROM {settings.DB_SCHEMA}.parking_requests
                       WHERE user_id = %s
                   ''', (user_id,))

                stats = cur.fetchone()

                return {
                    'total_user_requests': stats[0],
                    'accepted_spots_count': stats[1],
                    'canceled_spots_count': stats[2],
                    'not_found_spots_count': stats[3],
                }
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения статистики пользователя {user_id}: {e}"
            )
            return None

    def get_user_release_statistics(self, user_id):
        """
            Получение статистики по освобождениям мест пользователя
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                       SELECT 
                           COUNT(*) as total_user_releases,
                           COUNT(*) FILTER (WHERE status = 'ACCEPTED') as accepted_releases_count,
                           COUNT(*) FILTER (WHERE status = 'CANCELED') as canceled_releases_count,
                           COUNT(*) FILTER (WHERE status = 'NOT_FOUND') as not_found_releases_count
                       FROM {settings.DB_SCHEMA}.parking_releases
                       WHERE user_id = %s
                   ''', (user_id,))

                stats = cur.fetchone()

                return {
                    'total_user_releases': stats[0],
                    'accepted_releases_count': stats[1],
                    'canceled_releases_count': stats[2],
                    'not_found_releases_count': stats[3],
                }
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения статистики пользователя {user_id}: {e}"
            )
            return None

    def get_parking_transfers_by_date(self, rq_date: date):
        """
            Получить информацию о трансферах парковочных мест за указанную дату
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT pr.spot_id,
                                       recipient.tg_id AS recipient_tg_id,
                                       owner.tg_id     AS owner_tg_id
                                FROM {settings.DB_SCHEMA}.parking_releases pr
                                         JOIN {settings.DB_SCHEMA}.users owner ON pr.user_id = owner.user_id
                                         JOIN {settings.DB_SCHEMA}.users recipient ON pr.user_id_took = recipient.user_id
                                WHERE pr.release_date = %s
                                  AND pr.user_id_took IS NOT NULL
                                    AND pr.status = 'ACCEPTED';
                                ''', (rq_date,))

                return cur.fetchall()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения информации о трансферах парковочных мест за указанную дату: {e}"
            )
            return None

    def get_parking_transfers_by_date_range(self, start_date: date, end_date: date):
        """
            Получить информацию о передачах парковочных мест между пользователями за указанный период
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT pr.spot_id,
                                       recipient.tg_id AS recipient_tg_id,
                                       owner.tg_id     AS owner_tg_id
                                FROM {settings.DB_SCHEMA}.parking_releases pr
                                         JOIN {settings.DB_SCHEMA}.users owner ON pr.user_id = owner.user_id
                                         JOIN {settings.DB_SCHEMA}.users recipient ON pr.user_id_took = recipient.user_id
                                WHERE pr.release_date BETWEEN %s AND %s
                                  AND pr.user_id_took IS NOT NULL
                                  AND pr.status = 'ACCEPTED';
                                ''', (start_date, end_date,))

                return cur.fetchall()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения информации о передачах парковочных мест "
                            f"между пользователями за указанный период {start_date}-{end_date}: {e}"
            )

    def get_statistics_by_date_range(self, start_date: date, end_date: date):
        """
            Получение полной статистики по запросам и освобождениям за указанный период
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                WITH request_stats AS (
                                    SELECT 
                                        COUNT(*) as total,
                                        COUNT(*) FILTER (WHERE status = 'CANCELED') as canceled,
                                        COUNT(*) FILTER (WHERE status = 'NOT_FOUND') as not_found
                                    FROM {settings.DB_SCHEMA}.parking_requests
                                    WHERE request_date BETWEEN %s AND %s
                                ),
                                release_stats AS (
                                    SELECT 
                                        COUNT(*) as total,
                                        COUNT(*) FILTER (WHERE status = 'ACCEPTED') as accepted,
                                    FROM {settings.DB_SCHEMA}.parking_releases
                                    WHERE release_date BETWEEN %s AND %s
                                )
                                SELECT 
                                    rs.total, rs.canceled, rs.not_found,
                                    rels.total, rels.accepted
                                FROM request_stats rs, release_stats rels
                            ''', (start_date, end_date, start_date, end_date))

                stats = cur.fetchone()
                if not stats:
                    return []

                return {
                    'total_requests': stats[0],
                    'canceled_requests_count': stats[1],
                    'not_found_requests_count': stats[2],
                    'total_releases': stats[3],
                    'accepted_releases_count': stats[4],
                }
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения статистики по запросам "
                            f"и освобождениям за указанный период {start_date}-{end_date}: {e}"
            )
            return None
