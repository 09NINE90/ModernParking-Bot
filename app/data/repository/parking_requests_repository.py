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

        Выполняет SQL-запрос к таблице parking_requests для выборки всех записей,
        соответствующих указанному статусу и периоду времени между понедельником и пятницей.

        Args:
            cur: Курсор базы данных для выполнения SQL-запросов
            status (str): Статус заявок для фильтрации (например, 'ACCEPTED', 'CANCELED', 'NOT_FOUND')
            monday_date: Дата понедельника (начало периода)
            friday_date: Дата пятницы (конец периода)

        Returns:
            list[tuple]: Список кортежей с данными заявок, удовлетворяющих условиям.
                        Возвращает пустой список, если заявки не найдены.

        """
    cur.execute('''
                SELECT *
                FROM dont_touch.parking_requests pr
                WHERE pr.status = %s
                  AND pr.request_date >= %s
                    AND pr.request_date <= %s
                ''', (status, monday_date, friday_date))

    return cur.fetchall()