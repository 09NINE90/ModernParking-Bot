import logging

from app.data.db_config import DB_SCHEMA


async def insert_row_of_spot_confirmation(cur, user_id, release_id, request_id):
    """
        Асинхронно создает новую запись о подтверждении парковочного места.

        Вставляет новую запись в таблицу spot_confirmations с указанными параметрами.

        Параметры:
            cur: курсор базы данных для выполнения SQL-запросов
            user_id: UUID идентификатор пользователя
            release_id: UUID идентификатор записи об освобождении места
            request_id: UUID идентификатор запроса на парковку

        Возвращает:
            None: функция выполняет INSERT запрос и не возвращает данные

        Особенности:
            - Создает новую активную запись о подтверждении места
            - Используется для фиксации факта подтверждения парковки пользователем
            - Функция асинхронная, требует await при вызове
    """
    cur.execute(f"""
                INSERT INTO {DB_SCHEMA}.spot_confirmations (user_id, release_id, request_id)
                VALUES (%s, %s, %s)
                RETURNING id
                """, (user_id, release_id, request_id,))

    result = cur.fetchone()
    if result:
        return result[0]
    else:
        return None


async def set_message_sent_id(cur, spot_confirmation_id, message_sent_id):
    try:
        cur.execute(f"""
                            UPDATE {DB_SCHEMA}.spot_confirmations
                            SET message_sent_id = %s
                            WHERE id = %s
                            """,
                    (message_sent_id, spot_confirmation_id,))
    except Exception as e:
        logging.error(e)
        return None


async def get_message_sent_id(cur, user_id, release_id, request_id):
    try:
        cur.execute(f"""
                                SELECT message_sent_id 
                                FROM {DB_SCHEMA}.spot_confirmations 
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
        logging.error(e)
        return None


async def find_spot_confirmations_by_user(cur, user_id):
    """
        Асинхронно находит активное подтверждение парковочного места для пользователя.

        Выполняет поиск последней активной записи о подтверждении места для указанного пользователя
        с информацией о связанных сущностях.

        Параметры:
            cur: курсор базы данных для выполнения SQL-запросов
            user_id: UUID идентификатор пользователя

        Возвращает:
            tuple или None: кортеж с данными подтверждения в формате:
                - user_id: идентификатор пользователя
                - tg_id: Telegram ID пользователя
                - spot_id: идентификатор парковочного места
                - release_date: дата освобождения места
                - release_id: идентификатор записи об освобождении
                - request_id: идентификатор запроса на парковку
            или None, если активное подтверждение не найдено

        Особенности:
            - JOIN с таблицами users и parking_releases для получения дополнительной информации
            - Возвращает только последнюю активную запись (LIMIT 1)
            - Сортирует результаты по дате создания в порядке убывания
            - Фильтрует только активные записи (is_active = TRUE)
            - Функция асинхронная, требует await при вызове
    """
    cur.execute(f"""
                SELECT u.user_id, u.tg_id, prl.spot_id, prl.release_date, sc.release_id, sc.request_id
                FROM {DB_SCHEMA}.spot_confirmations sc
                         JOIN {DB_SCHEMA}.users u ON u.user_id = sc.user_id
                         JOIN {DB_SCHEMA}.parking_releases prl ON prl.id = sc.release_id
                WHERE sc.user_id = %s
                  AND sc.is_active = TRUE
                ORDER BY sc.created_at DESC
                LIMIT 1
                """, (user_id,))

    return cur.fetchone()


async def deactivate_spot_confirmations_by_user(cur, user_id):
    """
        Асинхронно деактивирует все активные подтверждения парковочных мест пользователя.

        Обновляет статус всех активных записей подтверждений для указанного пользователя
        на неактивный (is_active = FALSE) и устанавливает время обновления.

        Параметры:
            cur: курсор базы данных для выполнения SQL-запросов
            user_id: UUID идентификатор пользователя

        Возвращает:
            None: функция выполняет UPDATE запрос и не возвращает данные

        Особенности:
            - Деактивирует все активные подтверждения пользователя
            - Устанавливает время обновления на текущее (CURRENT_TIMESTAMP)
            - Используется для очистки старых подтверждений после обработки
            - Функция асинхронная, требует await при вызове
    """
    cur.execute(f"""
                UPDATE {DB_SCHEMA}.spot_confirmations
                SET is_active  = FALSE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id IN (SELECT user_id
                                  FROM {DB_SCHEMA}.users
                                  WHERE user_id = %s)
                  AND is_active = TRUE
                """, (user_id,))
