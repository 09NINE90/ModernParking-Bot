from contextlib import contextmanager
from datetime import date
from typing import Optional, Dict, Any

from psycopg2.extras import RealDictCursor

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

    def get_all_statistics_by_all_time(self):
        try:
            with self._get_cursor() as cur:
                cur.execute(
                    f'''
                            WITH request_stats AS (
                                SELECT 
                                    COUNT(*) as total,
                                    COUNT(*) FILTER (WHERE status = 'ACCEPTED') as accepted,
                                    COUNT(*) FILTER (WHERE status = 'PENDING') as pending,
                                    COUNT(*) FILTER (WHERE status = 'CANCELED') as canceled,
                                    COUNT(*) FILTER (WHERE status = 'NOT_FOUND') as not_found,
                                    COUNT(*) FILTER (WHERE status = 'WAITING_CONFIRMATION') as waiting_confirmation
                                FROM {settings.DB_SCHEMA}.parking_requests
                            ),
                            release_stats AS (
                                SELECT 
                                    COUNT(*) as total,
                                    COUNT(*) FILTER (WHERE status = 'ACCEPTED') as accepted,
                                    COUNT(*) FILTER (WHERE status = 'PENDING') as pending,
                                    COUNT(*) FILTER (WHERE status = 'CANCELED') as canceled,
                                    COUNT(*) FILTER (WHERE status = 'NOT_FOUND') as not_found,
                                    COUNT(*) FILTER (WHERE status = 'WAITING') as waiting
                                FROM {settings.DB_SCHEMA}.parking_releases
                            )
                            SELECT 
                                rs.total, rs.accepted, rs.pending, rs.canceled, rs.not_found, rs.waiting_confirmation,
                                rels.total, rels.accepted,  rels.pending, rels.canceled, rels.not_found, rels.waiting
                            FROM request_stats rs, release_stats rels
                        '''
                )

                stats = cur.fetchone()
                if not stats:
                    return []

                return {
                    'requests': {
                        'total': stats[0],
                        'accepted': stats[1],
                        'pending': stats[2],
                        'canceled': stats[3],
                        'not_found': stats[4],
                        'waiting_confirmation': stats[5],
                        'acceptance_rate': round((stats[1] / stats[0] * 100), 2) if stats[0] > 0 else 0,
                        'cancel_rate': round((stats[3] / stats[0] * 100), 2) if stats[0] > 0 else 0
                    },
                    'releases': {
                        'total': stats[6],
                        'accepted': stats[7],
                        'pending': stats[8],
                        'canceled': stats[9],
                        'not_found': stats[10],
                        'waiting': stats[11],
                        'acceptance_rate': round((stats[7] / stats[6] * 100), 2) if stats[6] > 0 else 0,
                        'cancel_rate': round((stats[9] / stats[6] * 100), 2) if stats[6] > 0 else 0
                    },
                }
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения полной статистики по запросам и освобождениям: {e}"
            )
            return None

    def get_parking_stats_by_period(self, period_type: str = "week", period_count: int = 1) -> Optional[Dict[str, Any]]:
        try:
            with self._get_cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT * FROM {settings.DB_SCHEMA}.get_parking_stats_by_period(%s, %s)
                    ORDER BY period_start DESC
                    LIMIT %s;
                    """,
                    (period_type, period_count, period_count),
                )
                return cur.fetchall()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка статистики по периодам: {e}"
            )
            return None
