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