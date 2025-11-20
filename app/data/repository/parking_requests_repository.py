from app.data.models.requests.requests_enum import ParkingRequestStatus


async def insert_request_on_date(cur, db_user_id, request_date):
    """
    Асинхронно создает запрос на парковку для указанной даты.

    Вставляет новую запись в таблицу parking_requests, если для данного пользователя
    и даты еще не существует активного запроса (использует механизм ON CONFLICT
    для предотвращения дубликатов).

    Параметры:
        cur: курсор базы данных для выполнения SQL-запросов
        db_user_id: UUID идентификатор пользователя в базе данных
        request_date: дата, на которую запрашивается парковка

    Возвращает:
        dict или None: словарь с полем 'id' новой записи, если вставка прошла успешно,
                      или None, если запись уже существовала (конфликт)

    Особенности:
        - Использует gen_random_uuid() для генерации уникального идентификатора записи
        - Конфликт определяется по комбинации (user_id, request_date)
        - При конфликте запрос игнорируется (DO NOTHING)
        - Функция асинхронная, требует await при вызове
    """
    cur.execute('''
                INSERT INTO dont_touch.parking_requests
                    (id, user_id, request_date)
                VALUES (gen_random_uuid(), %s, %s)
                ON CONFLICT (user_id, request_date) DO NOTHING
                RETURNING id
                ''', (db_user_id, request_date))

    return cur.fetchone()


async def parking_requests_by_week(cur, status, monday_date, friday_date):
    """
    Асинхронно получает заявки на парковку за указанную неделю по заданному статусу.

    Выполняет поиск всех записей в таблице parking_requests, соответствующих
    указанному статусу и периоду времени между понедельником и пятницей.

    Параметры:
        cur: курсор базы данных для выполнения SQL-запросов
        status: статус заявок для фильтрации (например, 'ACCEPTED', 'CANCELED', 'NOT_FOUND')
        monday_date: дата понедельника (начало периода, включительно)
        friday_date: дата пятницы (конец периода, включительно)

    Возвращает:
        list: список кортежей со всеми полями заявок на парковку, удовлетворяющих условиям

    Особенности:
        - Возвращает все поля таблицы parking_requests (*)
        - Фильтрация происходит по статусу и диапазону дат (включительно)
        - Используется для получения статистики заявок за конкретную неделю
        - Функция асинхронная, требует await при вызове
    """
    cur.execute('''
                SELECT *
                FROM dont_touch.parking_requests pr
                WHERE pr.status = %s
                  AND pr.request_date >= %s
                  AND pr.request_date <= %s
                ''', (status, monday_date, friday_date))

    return cur.fetchall()


async def all_parking_requests_by_status_and_user(cur, status, user_id):
    """
    Асинхронно получает все заявки на парковку пользователя по указанному статусу.

    Выполняет поиск всех записей в таблице parking_requests, соответствующих
    заданному статусу и идентификатору пользователя.

    Параметры:
        cur: курсор базы данных для выполнения SQL-запросов
        status: статус заявок для фильтрации (например, 'ACCEPTED', 'CANCELED', 'NOT_FOUND')
        user_id: UUID идентификатор пользователя в базе данных

    Возвращает:
        list: список кортежей со всеми полями заявок на парковку, удовлетворяющих условиям

    Особенности:
        - Возвращает все поля таблицы parking_requests (*)
        - Фильтрация происходит только по статусу и пользователю
        - Не ограничивает результаты по дате или другим параметрам
        - Используется для получения полной истории заявок пользователя по статусу
        - Функция асинхронная, требует await при вызове
    """
    cur.execute('''
                SELECT *
                FROM dont_touch.parking_requests pr
                WHERE pr.status = %s
                  AND pr.user_id = %s
                ''', (status, user_id,))

    return cur.fetchall()


async def current_spots_request_by_user(cur, user_id, request_date):
    """
    Асинхронно получает актуальные запросы на парковочные места пользователя.

    Выполняет поиск активных и ожидающих запросов на парковку для указанного пользователя,
    начиная с заданной даты.

    Параметры:
        cur: курсор базы данных для выполнения SQL-запросов
        user_id: UUID идентификатор пользователя в базе данных
        request_date: минимальная дата запроса для фильтрации (включительно)

    Возвращает:
        list: список кортежей с данными запросов, где каждый кортеж содержит:
            - status: статус запроса ('ACCEPTED' или 'PENDING')
            - request_date: дата запроса на парковку

    Особенности:
        - Фильтрует записи со статусами 'ACCEPTED' и 'PENDING'
        - Исключает отмененные и завершенные запросы
        - Результаты сортируются по дате запроса в порядке убывания (сначала новые)
        - Используется для отображения актуальных запросов в статистике пользователя
        - Функция асинхронная, требует await при вызове
    """
    cur.execute('''
                SELECT pr.status, pr.request_date
                FROM dont_touch.parking_requests pr
                WHERE pr.user_id = %s
                  AND pr.request_date >= %s
                  AND (pr.status = 'ACCEPTED' OR pr.status = 'PENDING')
                ORDER BY request_date DESC
                ''', (user_id, request_date,))

    return cur.fetchall()

async def find_user_requests_for_revoke(cur, db_user_id, date):
    """
        Асинхронно находит запросы на парковку пользователя для возможного отзыва.

        Выполняет поиск активных и ожидающих запросов на парковку, начиная с указанной даты,
        с информацией о связанных освобождениях мест.

        Параметры:
            cur: курсор базы данных для выполнения SQL-запросов
            db_user_id: UUID идентификатор пользователя в базе данных
            date: дата, начиная с которой осуществляется поиск запросов (включительно)

        Возвращает:
            list: список кортежей с данными запросов, где каждый кортеж содержит:
                - id: идентификатор запроса на парковку
                - request_date: дата запроса
                - status: статус запроса ('ACCEPTED' или 'PENDING')
                - spot_id: идентификатор привязанного места парковки (может быть None)

        Особенности:
            - Ищет записи со статусами 'ACCEPTED' и 'PENDING'
            - LEFT JOIN с таблицей parking_releases для поиска связанных освобождений мест
            - Результаты сортируются по дате запроса в возрастающем порядке
            - Используется для функциональности отзыва/аннулирования запросов на парковку
            - Функция асинхронная, требует await при вызове
    """
    cur.execute('''
                SELECT pr.id,
                       pr.request_date,
                       pr.status,
                       prel.spot_id
                FROM dont_touch.parking_requests pr
                         LEFT JOIN dont_touch.parking_releases prel
                                   ON pr.user_id = prel.user_id_took
                                       AND pr.request_date = prel.release_date
                                       AND prel.status = 'ACCEPTED'
                WHERE pr.user_id = %s
                  AND pr.request_date >= %s
                  AND pr.status IN ('ACCEPTED', 'PENDING')
                ORDER BY pr.request_date
                ''', (db_user_id, date,))

    return cur.fetchall()

async def find_request_for_confirm_revoke(cur, db_user_id, request_id):
    """
        Асинхронно находит конкретный запрос на парковку для подтверждения отзыва.

        Выполняет поиск конкретного запроса на парковку по ID пользователя и ID запроса,
        с информацией о связанных освобождениях мест.

        Параметры:
            cur: курсор базы данных для выполнения SQL-запросов
            db_user_id: UUID идентификатор пользователя в базе данных
            request_id: UUID идентификатор запроса на парковку

        Возвращает:
            tuple или None: кортеж с данными запроса в следующем формате:
                - id: идентификатор запроса на парковку
                - request_date: дата запроса
                - status: статус запроса
                - spot_id: идентификатор привязанного места парковки
                - prel.id: идентификатор записи об освобождении места
            или None, если запрос не найден

        Особенности:
            - Ищет конкретный запрос по комбинации user_id и request_id
            - LEFT JOIN с таблицей parking_releases для поиска связанных освобождений мест
            - Ограничивает результат одной записью (LIMIT 1)
            - Используется для подтверждения отзыва запроса на парковку
            - Функция асинхронная, требует await при вызове
    """
    cur.execute('''
                SELECT pr.id,
                       pr.request_date,
                       pr.status,
                       prel.spot_id,
                       prel.id
                FROM dont_touch.parking_requests pr
                         LEFT JOIN dont_touch.parking_releases prel
                                   ON pr.user_id = prel.user_id_took
                                       AND pr.request_date = prel.release_date
                                       AND prel.status = 'ACCEPTED'
                WHERE pr.user_id = %s
                  AND pr.id = %s
                LIMIT 1
                ''', (db_user_id, request_id,))

    return cur.fetchone()


async def update_parking_request_status(cur, request_id, current_status: ParkingRequestStatus):
    """
    Обновляет статус запроса на парковку.

    Изменяет статус запроса на указанный и фиксирует время обработки.

    Параметры:
        cur: курсор базы данных для выполнения SQL-запросов
        request_id: UUID запроса в таблице parking_requests
        current_status: новый статус для установки ('ACCEPTED', 'CANCELED', 'NOT_FOUND', 'PENDING')

    Логика:
        - Устанавливает указанный статус для запроса
        - Фиксирует время обработки в processed_at
        - Обновляет только указанный запрос по ID

    Особенности:
        - Универсальный метод для изменения статуса запроса
        - CURRENT_TIMESTAMP гарантирует единое время на сервере БД
        - Поддерживает все валидные статусы: PENDING, ACCEPTED, CANCELED, NOT_FOUND
        - Асинхронная функция, требует await при вызове
    """
    cur.execute('''
                UPDATE dont_touch.parking_requests
                SET status       = %s,
                    processed_at = CURRENT_TIMESTAMP
                WHERE id = %s
                ''', (current_status.name, request_id,))