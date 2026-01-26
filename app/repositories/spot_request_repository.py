from contextlib import contextmanager
from datetime import date

from app.config import settings
from app.data.models.enumz.requests_statuses_enum import ParkingRequestStatus
from app.logs.log_builder import log_sync


class SpotRequestRepository:
    """Репозиторий для работы с парковочными местами"""

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

    def get_user_request_dates(self, user_id, from_date):
        """
            Получает список дат, на которые пользователь уже создал запросы на парковку.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT request_date FROM {settings.DB_SCHEMA}.parking_requests 
                                WHERE user_id = %s 
                                    AND request_date >= %s
                                ''', (user_id, from_date,))
                return cur.fetchall()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения списка дат, на которые пользователь "
                            f"уже создал запросы на освобождение парковочного места.: {e}"
            )
            return False

    def insert_request_on_date(self, db_user_id, request_date, is_auto_request):
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                INSERT INTO {settings.DB_SCHEMA}.parking_requests
                                    (id, user_id, request_date, is_auto_request)
                                VALUES (gen_random_uuid(), %s, %s, %s)
                                ON CONFLICT (user_id, request_date) DO NOTHING
                                RETURNING id
                                ''', (db_user_id, request_date, is_auto_request))

                return cur.fetchone() is not None
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения списка дат, на которые пользователь "
                            f"уже создал запросы на освобождение парковочного места: {e}"
            )
            return False

    def get_spot_candidates(self, rq_date: date, limit: int):
        """
            Получает список кандидатов для распределения свободных мест на указанную дату.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT prq.id as request_id, prq.user_id, u.rating, u.tg_id
                                FROM {settings.DB_SCHEMA}.parking_requests prq
                                         JOIN {settings.DB_SCHEMA}.users u ON prq.user_id = u.user_id
                                WHERE prq.request_date = %s
                                  AND prq.status = 'PENDING'
                                  AND NOT EXISTS (SELECT 1
                                                  FROM {settings.DB_SCHEMA}.parking_releases prl
                                                  WHERE prl.user_id = prq.user_id
                                                    AND prl.release_date = %s
                                                    AND prl.status = 'PENDING')
                                ORDER BY u.rating
                                LIMIT %s
                                ''', (rq_date, rq_date, limit))

                return cur.fetchall()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения списка кандидатов "
                            f"для распределения свободных мест на указанную дату.: {e}"
            )
            return False

    def get_all_spot_candidates(self, rq_date: date):
        """
        Получает ВСЕХ кандидатов для распределения на указанную дату
        только со статусом PENDING.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                    SELECT prq.id as request_id, prq.user_id, u.rating, u.tg_id
                    FROM {settings.DB_SCHEMA}.parking_requests prq
                    JOIN {settings.DB_SCHEMA}.users u ON prq.user_id = u.user_id
                    WHERE prq.request_date = %s
                      AND prq.status = 'PENDING'
                      AND NOT EXISTS (
                          SELECT 1
                          FROM {settings.DB_SCHEMA}.parking_releases prl
                          WHERE prl.user_id = prq.user_id
                            AND prl.release_date = %s
                            AND prl.status IN ('PENDING', 'ACCEPTED', 'WAITING')
                      )
                    ORDER BY u.rating
                ''', (rq_date, rq_date))

                return cur.fetchall()
        except Exception as e:
            log_sync(log_message=f"Ошибка получения всех кандидатов: {e}")
            return []

    def update_parking_request_status(self, request_id, current_status: ParkingRequestStatus):
        """
            Обновляет статус запроса на парковку.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                        UPDATE {settings.DB_SCHEMA}.parking_requests
                        SET status       = %s,
                            processed_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        ''', (current_status.name, request_id,))

        except Exception as e:
            log_sync(
                log_message=f"Ошибка обновления статуса запроса на место: {e}"
            )
            return False

    def get_request_status_by_id(self, request_id):
        """
            Получает статус запроса на место по ID
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT pr.status FROM {settings.DB_SCHEMA}.parking_requests pr
                                WHERE pr.id = %s 
                                ''', (request_id,))

                result = cur.fetchone()
                return result[0] if result else None
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения статуса запроса на место по ID: {e}"
            )
            return False

    def find_user_requests_for_revoke(self, db_user_id, rq_date: date):
        """
            Получает список запросов на парковочные места пользователя,
            которые можно отозвать
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT pr.id,
                                       pr.request_date,
                                       pr.status,
                                       prel.spot_id
                                FROM {settings.DB_SCHEMA}.parking_requests pr
                                         LEFT JOIN {settings.DB_SCHEMA}.parking_releases prel
                                                   ON pr.user_id = prel.user_id_took
                                                       AND pr.request_date = prel.release_date
                                                       AND prel.status = 'ACCEPTED'
                                WHERE pr.user_id = %s
                                  AND pr.request_date >= %s
                                  AND pr.status IN ('ACCEPTED', 'PENDING')
                                ORDER BY pr.request_date
                                ''', (db_user_id, rq_date,))

                return cur.fetchall()
        except Exception as e:
            log_sync(
                log_message="Ошибка получения списка запросов на парковочные места пользователя, "
                            f"которые можно отозвать: {e}"
            )
            return None

    def find_request_for_confirm_revoke(self, db_user_id, request_id):
        """
            Находит конкретный запрос на парковку для подтверждения отзыва
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT pr.id,
                                       pr.request_date,
                                       pr.status,
                                       prel.spot_id,
                                       prel.id
                                FROM {settings.DB_SCHEMA}.parking_requests pr
                                         LEFT JOIN {settings.DB_SCHEMA}.parking_releases prel
                                                   ON pr.user_id = prel.user_id_took
                                                       AND pr.request_date = prel.release_date
                                                       AND prel.status = 'ACCEPTED'
                                WHERE pr.user_id = %s
                                  AND pr.id = %s
                                LIMIT 1
                                ''', (db_user_id, request_id,))

                return cur.fetchone()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения запроса на парковку для подтверждения отзыва: {e}"
            )
            return None

    def get_current_spots_request_by_user(self, user_id, rq_date: date):
        """
            Получить актуальные запросы на места
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT 
                                    pr.status, 
                                    pr.request_date,
                                    CASE 
                                        WHEN pr.status = 'ACCEPTED' THEN (
                                            SELECT spot_id 
                                            FROM {settings.DB_SCHEMA}.parking_releases prel 
                                            WHERE prel.user_id_took = pr.user_id 
                                                AND prel.release_date = pr.request_date
                                                AND prel.status = 'ACCEPTED'
                                            LIMIT 1
                                        )
                                        ELSE NULL
                                    END as spot_id
                                FROM {settings.DB_SCHEMA}.parking_requests pr
                                WHERE pr.user_id = %s
                                    AND pr.request_date >= %s
                                    AND (pr.status = 'ACCEPTED' OR pr.status = 'PENDING')
                                ORDER BY request_date DESC
                            ''', (user_id, rq_date,))

                return cur.fetchall()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения актуальных запросов на места пользователя {user_id}: {e}"
            )

    def update_requests_statuses_to_not_found_by_date(self, rq_date: date):
        """
            Переводит все запросы в статус NOT_FOUND, если:
            - их текущий статус PENDING,
            - их дата меньше указанной даты (просроченные запросы).
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                            UPDATE {settings.DB_SCHEMA}.parking_requests
                            SET status = 'NOT_FOUND'
                            WHERE status = 'PENDING'
                                AND request_date < %s
                            ''',
                            (rq_date,))
        except Exception as e:
            log_sync(
                log_message=f"Ошибка обновления статусов запросов: {e}"
            )

    def update_requests_statuses_to_canceled_by_date(self, rq_date: date):
        """
            Переводит все запросы в статус CANCELED, если:
            - их текущий статус PENDING или WAITING_CONFIRMATION,
            - их дата меньше указанной даты (просроченные запросы).
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                    UPDATE {settings.DB_SCHEMA}.parking_requests
                                    SET status = 'CANCELED'
                                    WHERE status = 'PENDING' OR status = 'WAITING_CONFIRMATION'
                                        AND request_date < %s
                                    ''',
                            (rq_date,))
        except Exception as e:
            log_sync(
                log_message=f"Ошибка обновления статусов запросов: {e}"
            )

    def bulk_cancel_requests_by_confirmations(self, confirmations):
        """
            Переводит связанные с подтверждениями запросы в статус CANCELED.
            confirmations: iterable[(conf_id, user_id, request_id, release_id, message_id, tg_id)]
        """
        request_ids = {c[2] for c in confirmations}
        if not request_ids:
            return None

        try:
            with self._get_cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE {settings.DB_SCHEMA}.parking_requests
                    SET status = 'CANCELED',
                        processed_at = CURRENT_TIMESTAMP
                    WHERE id = ANY(%s::uuid[])
                    """,
                    (list(request_ids),),
                )
        except Exception as e:
            log_sync(
                log_message=f"Ошибка массового обновления статуса запросов в CANCELED: {e}"
            )
            return None
