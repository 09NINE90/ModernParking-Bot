from datetime import date
from typing import Optional
from contextlib import contextmanager
from psycopg2.extras import RealDictCursor

from app.config import settings
from app.data.models.enumz.releases_statuses_enum import ParkingReleaseStatus
from app.logs.log_builder import log_sync


class SpotReleaseRepository:
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

    def get_active_spot_by_id(self, spot_id: int) -> Optional[dict]:
        """Получает место по ID"""
        try:
            with self._get_cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT *
                    FROM {settings.DB_SCHEMA}.parking_spots
                    WHERE spot_id = %s
                    AND is_active = TRUE
                    """,
                    (spot_id,)
                )
                return cur.fetchone()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения места {spot_id}: {e}"
            )
            return None

    def insert_spot_on_date(self, db_user_id: str, spot_id: int, release_date: date) -> bool:
        """
        Сохраняет освобождение места на дату

        Returns:
            bool: True если успешно создано, False если уже существует
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO {settings.DB_SCHEMA}.parking_releases (id, user_id, spot_id, release_date)
                    VALUES (gen_random_uuid(), %s, %s, %s)
                    ON CONFLICT (spot_id, release_date) DO NOTHING
                    RETURNING id
                    """,
                    (db_user_id, spot_id, release_date)
                )
                return cur.fetchone() is not None
        except Exception as e:
            log_sync(
                log_message=f"Ошибка сохранения освобождения места: {e}"
            )
            return False

    def get_user_spot_by_date(self, request_date, db_user_id):
        """
            Проверяет, получил ли пользователь место на парковке на указанную дату.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT 1
                                FROM {settings.DB_SCHEMA}.parking_releases
                                WHERE release_date = %s
                                  AND user_id_took = %s
                                  AND status = 'ACCEPTED'
                                ''', (request_date, db_user_id))
                return cur.fetchone()

        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения данных о парковочном месте пользователя: {e}"
            )
            return False

    def get_spot_id_by_user_id_and_request_date(self, request_date, db_user_id):
        """
            Получает идентификатор парковочного места, закрепленного за пользователем на указанную дату.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT spot_id
                                FROM {settings.DB_SCHEMA}.parking_releases
                                WHERE release_date = %s
                                  AND user_id_took = %s
                                  AND status = 'ACCEPTED'
                                ORDER BY created_at ASC
                                ''', (request_date, str(db_user_id),))

                return cur.fetchone()

        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения данных о парковочном месте, "
                            f"закрепленного за пользователем на указанную дату: {e}"
            )
            return False

    def get_free_parking_releases_by_date(self, rq_date):
        """
            Получает список свободных парковочных мест на указанную дату.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT *
                                FROM {settings.DB_SCHEMA}.parking_releases pr
                                WHERE pr.status = 'PENDING'
                                  AND pr.release_date = %s
                                ''', (rq_date,))

                return cur.fetchall()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения списка свободных парковочных мест на указанную дату: {e}"
            )
            return None

    def parking_releases_between_two_dates(self, status, first_date, last_date):
        """
            Получает записи о возврате парковочных мест за указанную неделю по заданному статусу.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT *
                                FROM {settings.DB_SCHEMA}.parking_releases pr
                                WHERE pr.status = %s
                                  AND pr.release_date >= %s
                                  AND pr.release_date <= %s
                                ''', (status, first_date, last_date))

                return cur.fetchall()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения записи о возврате парковочных мест "
                            f"за указанную неделю по заданному статусу.: {e}"
            )
            return False

    def get_user_releases_dates(self, user_id, spot_id, from_date):
        """
            Получает список дат, на которые пользователь уже создал запросы на освобождение парковочного места.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT release_date FROM {settings.DB_SCHEMA}.parking_releases 
                                WHERE user_id = %s 
                                    AND spot_id = %s
                                    AND release_date >= %s
                                ''', (user_id, spot_id, from_date,))
                return cur.fetchall()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения списка дат, на которые пользователь "
                            f"уже создал запросы на освобождение парковочного места.: {e}"
            )
            return False

    def get_dates_with_availability(self):
        """
            Получает список дат, на которые есть доступные парковочные места и ожидающие запросы.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT DISTINCT pr.release_date
                                FROM {settings.DB_SCHEMA}.parking_releases pr
                                WHERE pr.status = 'PENDING'
                                  AND EXISTS (SELECT 1
                                              FROM {settings.DB_SCHEMA}.parking_requests prq
                                              WHERE prq.request_date = pr.release_date
                                                AND prq.status = 'PENDING')
                                ''')

                result = cur.fetchall()
                if result:
                    return [row[0] for row in result]
                else:
                    return None
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения списка дат, на которые есть "
                            f"доступные парковочные места и ожидающие запросы.: {e}"
            )
            return None

    def get_free_spots_by_date(self, rq_date: date):
        """
           Получает список свободных парковочных мест на указанную дату.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                            SELECT id, spot_id
                            FROM {settings.DB_SCHEMA}.parking_releases
                            WHERE release_date = %s
                              AND status = 'PENDING'
                            ORDER BY created_at
                            ''', (rq_date,))

                result = cur.fetchall()
                if result:
                    return result
                else:
                    return None
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения списка свободных парковочных мест на указанную дату.: {e}"
            )
            return None

    def is_spot_still_available(self, release_id):
        """Проверяет, что место все еще доступно для распределения"""
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                    SELECT status FROM {settings.DB_SCHEMA}.parking_releases 
                    WHERE id = %s 
                        AND status = 'PENDING'
                """, (release_id,))

                return cur.fetchone() is not None
        except Exception as e:
            log_sync(
                log_message=f"Ошибка проверки места на доступность: {e}"
            )
            return False

    def update_parking_releases(self, user_id, release_id, current_status: ParkingReleaseStatus):
        """
            Обновляет статус релиза места и назначает пользователя на это место
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                        UPDATE {settings.DB_SCHEMA}.parking_releases
                        SET user_id_took = %s,
                            status       = %s,
                            updated_at   = CURRENT_TIMESTAMP
                        WHERE id = %s
                        RETURNING id
                        ''', (user_id, current_status.name, release_id))

        except Exception as e:
            log_sync(
                log_message=f"Ошибка обновления статуса релиза места и назначения пользователя на это место: {e}"
            )
            return False

    def update_release_status(self, release_id, current_status: ParkingReleaseStatus):
        """
            Обновляет статус релиза места
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                UPDATE {settings.DB_SCHEMA}.parking_releases
                                SET status       = %s,
                                    updated_at   = CURRENT_TIMESTAMP
                                WHERE id = %s
                                RETURNING id
                                ''', (current_status.name, release_id))

        except Exception as e:
            log_sync(
                log_message=f"Ошибка обновления статуса релиза места: {e}"
            )
            return False

    def accept_spot_if_free(self, release_id, user_id) -> bool:
        """
            Пытается занять место только если оно ещё в статусе WAITING и без user_id.
            Возвращает True, если удалось (пользователь успел первым).
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                    UPDATE {settings.DB_SCHEMA}.parking_releases
                    SET status = 'ACCEPTED', 
                        user_id_took = %s,
                        updated_at   = CURRENT_TIMESTAMP
                    WHERE id = %s
                      AND status = 'WAITING'
                    RETURNING id
                """, (user_id, release_id))
                row = cur.fetchone()
                return bool(row)
        except Exception as e:
            log_sync(log_message=f"Ошибка при попытке занять место: {e}")
            return False

    def get_release_owner(self, release_id):
        """
            Получает информацию о пользователе, который освободил парковочное место.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT pr.user_id, u.tg_id
                                FROM {settings.DB_SCHEMA}.parking_releases pr
                                         JOIN {settings.DB_SCHEMA}.users u ON pr.user_id = u.user_id
                                WHERE pr.id = %s
                                ''', (release_id,))

                result = cur.fetchone()
                if result:
                    return result
                else:
                    return None
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения информации о пользователе, который освободил парковочное место: {e}"
            )
            return False

    def get_release_status_by_id(self, release_id):
        """
            Получает статус освобождения места по ID
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT pr.status FROM {settings.DB_SCHEMA}.parking_releases pr
                                WHERE pr.id = %s 
                                ''', (release_id,))

                result = cur.fetchone()
                return result[0] if result else None
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения статуса освобождения места по ID: {e}"
            )
            return False

    def update_parking_release_set_free(self, release_id, current_status: ParkingReleaseStatus):
        """
            Обновляет запрос на освобождение места при отзыве.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                        UPDATE {settings.DB_SCHEMA}.parking_releases
                        SET user_id_took = NULL,
                            status       = %s,
                            updated_at   = CURRENT_TIMESTAMP
                        WHERE id = %s
                        ''', (current_status.name, release_id))
        except Exception as e:
            log_sync(
                log_message=f"Ошибка обновления запроса на освобождение места при отзыве: {e}"
            )
            return False

    def find_user_releases_for_revoke(self, db_user_id, rq_date: date):
        """
            Находит запросы на освобождение мест пользователя для возможного отзыва.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT prel.id,
                                       prel.release_date,
                                       prel.status,
                                       prel.spot_id
                                FROM {settings.DB_SCHEMA}.parking_releases prel
                                WHERE prel.user_id = %s
                                  AND prel.release_date >= %s
                                  AND prel.status = 'PENDING'
                                ORDER BY prel.release_date
                                ''', (db_user_id, rq_date,))

                return cur.fetchall()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения запросов на освобождение "
                            f"мест пользователя для возможного отзыва: {e}"
            )
            return False

    def find_release_for_confirm_revoke(self, db_user_id, release_id):
        """
            Находит запрос на освобождение места для подтверждения отзыва.
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT prel.id,
                                       prel.release_date,
                                       prel.status,
                                       prel.spot_id
                                FROM {settings.DB_SCHEMA}.parking_releases prel
                                WHERE prel.user_id = %s
                                  AND prel.id = %s
                                LIMIT 1
                                ''', (db_user_id, release_id,))

                return cur.fetchone()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения запроса на освобождение "
                            f"места для подтверждения отзыва {e}"
            )
            return False

    def get_current_spots_releases_by_user(self, user_id, rq_date: date):
        """
            Получить актуальные освобожденные места пользователя
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                                SELECT pr.spot_id, pr.status, pr.release_date
                                FROM {settings.DB_SCHEMA}.parking_releases pr
                                WHERE pr.user_id = %s
                                  AND pr.release_date >= %s
                                  AND (pr.status = 'ACCEPTED' OR pr.status = 'PENDING' OR pr.status = 'WAITING')
                                ORDER BY release_date DESC
                                ''', (user_id, rq_date,))

                return cur.fetchall()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения актуальных освобожденных мест пользователя {user_id}: {e}"
            )

    def get_count_waiting_releases_by_date(self, rq_date: date):
        """
            Получение количества мест, ожидающих подтверждения
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                            SELECT COUNT(*) FROM {settings.DB_SCHEMA}.parking_releases
                            WHERE release_date >= %s 
                                AND status = 'WAITING' 
                            ''', (rq_date,))
                return cur.fetchone()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения количества мест,ожидающих подтверждения: {e}"
            )

    def get_accepted_spot_by_date(self, rq_date: date):
        """
            Получение принятых мест в конкретную дату
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f"""
                                SELECT prel.spot_id, u.tg_id, u.user_id, prel.id, prel.release_date, prq.id
                                FROM {settings.DB_SCHEMA}.parking_releases prel
                                         JOIN {settings.DB_SCHEMA}.users u ON prel.user_id_took = u.user_id
                                         JOIN {settings.DB_SCHEMA}.parking_requests prq
                                              ON prq.user_id = prel.user_id_took 
                                                  AND prq.request_date = prel.release_date
                                WHERE prel.status = 'ACCEPTED'
                                  AND prel.release_date = %s
                                """, (rq_date,))

                return cur.fetchall()
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения принятых мест в конкретную дату {rq_date}: {e}"
            )

    def update_releases_statuses_to_not_found_by_date(self, rq_date: date):
        """
            Переводит все релизы в статус NOT_FOUND, если:
            - их текущий статус PENDING,
            - их дата меньше указанной даты (просроченные релизы).
        """
        try:
            with self._get_cursor() as cur:
                cur.execute(f'''
                            UPDATE {settings.DB_SCHEMA}.parking_releases
                            SET status = 'NOT_FOUND',
                                updated_at   = CURRENT_TIMESTAMP
                            WHERE status = 'PENDING'
                                AND release_date < %s
                            ''',
                            (rq_date,))
        except Exception as e:
            log_sync(
                log_message=f"Ошибка обновления статусов релизов: {e}"
            )

    def mark_releases_not_found_if_only_cancelled(self, confirmations):
        """
            Переводит релизы в NOT_FOUND, если они связаны с подтверждениями,
            которые мы сейчас отменяем, и при этом сами релизы ещё в статусах
            PENDING или WAITING.
            confirmations: iterable[(conf_id, user_id, request_id, release_id, message_id, tg_id)]
        """
        release_ids = {c[3] for c in confirmations}  # уникальные release_id
        if not release_ids:
            return None

        try:
            with self._get_cursor() as cur:
                cur.execute(
                    f"""
                        UPDATE {settings.DB_SCHEMA}.parking_releases prl
                        SET status = 'NOT_FOUND',
                            updated_at   = CURRENT_TIMESTAMP
                        WHERE prl.id = ANY(%s::uuid[])
                          AND prl.status IN ('PENDING', 'WAITING')
                          AND NOT EXISTS (
                              SELECT 1
                              FROM {settings.DB_SCHEMA}.spot_confirmations sc
                              WHERE sc.release_id = prl.id
                                AND sc.status = 'WAITING'
                          )
                        """,
                    (list(release_ids),),
                )
        except Exception as e:
            log_sync(
                log_message=f"Ошибка массового обновления релизов в NOT_FOUND: {e}"
            )
            return None
