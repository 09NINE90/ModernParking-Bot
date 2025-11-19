from app.data.models.releases.releases_enum import ParkingReleaseStatus


async def get_user_spot_by_date(cur, request_date, db_user_id):
    """
    Проверяет, получил ли пользователь место на парковке на указанную дату.

    Выполняет поиск в таблице освобожденных парковочных мест (parking_releases),
    чтобы определить, было ли закреплено место за пользователем на конкретную дату.

    Параметры:
        cur: курсор базы данных для выполнения SQL-запросов
        request_date: дата, для которой проверяется наличие парковочного места
        db_user_id: UUID идентификатор пользователя в базе данных

    Возвращает:
        dict или None:
            - Словарь с полем '1' (значение 1), если пользователь получил место на указанную дату
            - None, если место не было предоставлено

    Логика:
        - Ищет записи где release_date совпадает с запрашиваемой датой
        - И где данный пользователь является получателем места (user_id_took)
        - Возвращает простой индикатор наличия (1), а не полные данные записи

    Особенности:
        - Функция возвращает только факт наличия/отсутствия, без деталей о месте
        - Используется для проверки прав доступа или статуса бронирования
        - Асинхронная функция, требует await при вызове
    """
    cur.execute('''
                SELECT 1
                FROM dont_touch.parking_releases
                WHERE release_date = %s
                  AND user_id_took = %s
                  AND status = 'ACCEPTED'
                ''', (request_date, db_user_id))
    return cur.fetchone()


async def get_spot_id_by_user_id_and_request_date(cur, db_user_id, request_date):
    """
        Получает идентификатор парковочного места, закрепленного за пользователем на указанную дату.

        Выполняет поиск в таблице распределения парковочных мест (parking_releases),
        чтобы определить какое конкретное место было назначено пользователю на заданную дату.

        Параметры:
            cur: курсор базы данных для выполнения SQL-запросов
            db_user_id: UUID идентификатор пользователя в базе данных
            request_date: дата, для которой запрашивается идентификатор парковочного места

        Возвращает:
            dict или None:
                - Словарь с полем 'spot_id', содержащим идентификатор парковочного места
                - None, если пользователю не было назначено место на указанную дату

        Логика:
            - Ищет записи где release_date совпадает с запрашиваемой датой
            - И где данный пользователь является получателем места (user_id_took)
            - Сортирует результаты по времени создания (created_at) в порядке возрастания
            - Возвращает первую найденную запись (самую раннюю)

        Особенности:
            - Возвращает конкретный spot_id, а не просто факт наличия
            - ORDER BY created_at ASC гарантирует детерминированность при множественных записях
            - Явное преобразование db_user_id в string (str(db_user_id))
            - Асинхронная функция, требует await при вызове
        """
    cur.execute('''
                SELECT spot_id
                FROM dont_touch.parking_releases
                WHERE release_date = %s
                  AND user_id_took = %s
                  AND status = 'ACCEPTED'
                ORDER BY created_at ASC
                ''', (request_date, str(db_user_id),))

    return cur.fetchone()


async def insert_spot_on_date(cur, db_user_id, spot_num, release_date):
    """
    Асинхронно создает запись об освобождении парковочного места на указанную дату.

    Вставляет новую запись в таблицу parking_releases, резервируя конкретное
    парковочное место за пользователем на определенную дату.

    Параметры:
        cur: курсор базы данных для выполнения SQL-запросов
        db_user_id: UUID идентификатор пользователя, который освобождает/резервирует место
        spot_num: идентификатор парковочного места (номер или UUID)
        release_date: дата, на которую освобождается/резервируется место

    Возвращает:
        dict или None: словарь с полем 'id' новой записи, если вставка прошла успешно,
                      или None, если место на эту дату уже занято (конфликт)

    Логика:
        - Создает запись о привязке пользователя к парковочному месту на конкретную дату
        - Использует механизм ON CONFLICT для предотвращения двойного бронирования места
        - Конфликт определяется по комбинации (spot_id, release_date)

    Особенности:
        - Использует gen_random_uuid() для генерации уникального идентификатора записи
        - При конфликте (место уже занято на эту дату) запрос игнорируется (DO NOTHING)
        - Функция асинхронная, требует await при вызове
        - Не заполняет поле user_id_took (получатель места), только user_id (инициатор)
    """
    cur.execute('''
                INSERT INTO dont_touch.parking_releases
                    (id, user_id, spot_id, release_date)
                VALUES (gen_random_uuid(), %s, %s, %s)
                ON CONFLICT (spot_id, release_date) DO NOTHING
                RETURNING id
                ''', (db_user_id, spot_num, release_date))

    return cur.fetchone()


async def get_user_id_took_by_date_and_spot(cur, db_user_id, spot_number, release_date):
    """
    Получает идентификатор пользователя, который получил парковочное место от указанного владельца.

    Выполняет поиск в таблице parking_releases, чтобы определить, кому было передано
    конкретное парковочное место от определенного пользователя на указанную дату.

    Параметры:
        cur: курсор базы данных для выполнения SQL-запросов
        db_user_id: UUID идентификатор пользователя-владельца (тот, кто освободил место)
        spot_number: идентификатор парковочного места
        release_date: дата передачи парковочного места

    Возвращает:
        dict или None:
            - Словарь с полем 'user_id_took', содержащим UUID пользователя-получателя
            - None, если место не было передано никому (user_id_took is NULL)
            - None, если запись не найдена

    Логика:
        - Ищет запись где release_date, user_id (владелец) и spot_id совпадают с параметрами
        - Возвращает идентификатор пользователя, который получил это место (user_id_took)

    Особенности:
        - Функция проверяет факт передачи места от конкретного владельца конкретному получателю
        - Может использоваться для проверки, было ли место уже занято кем-то
        - user_id_took будет NULL если место освобождено, но еще никем не занято
        - Асинхронная функция, требует await при вызове
    """
    cur.execute('''
                SELECT pr.user_id_took
                FROM dont_touch.parking_releases pr
                WHERE pr.release_date = %s
                  AND pr.user_id = %s
                  AND pr.spot_id = %s
                  AND pr.status = 'ACCEPTED'
                ''', (release_date, db_user_id, spot_number))

    return cur.fetchone()


async def free_parking_releases_by_date(cur, date):
    """
        Получает список свободных парковочных мест на указанную дату.

        Выполняет поиск всех освобожденных мест, которые еще не были заняты пользователями.

        Параметры:
            cur: курсор базы данных
            date: дата для поиска свободных мест

        Возвращает:
            list: список всех свободных парковочных мест на указанную дату
        """
    cur.execute('''
                SELECT *
                FROM dont_touch.parking_releases pr
                WHERE pr.status = 'PENDING'
                  AND pr.release_date = %s
                ''', (date,))

    return cur.fetchall()


async def parking_releases_by_week(cur, status, monday_date, friday_date):
    """
    Асинхронно получает записи о возврате парковочных мест за указанную неделю по заданному статусу.

    Выполняет SQL-запрос к таблице parking_releases для выборки всех записей,
    соответствующих указанному статусу и периоду времени между понедельником и пятницей.

    Args:
        cur: Курсор базы данных для выполнения SQL-запросов
        status (str): Статус записей о возврате для фильтрации (например, 'ACCEPTED', 'NOT_FOUND')
        monday_date: Дата понедельника (начало периода)
        friday_date: Дата пятницы (конец периода)

    Returns:
        list[tuple]: Список кортежей с данными о возвратах, удовлетворяющих условиям.
                    Возвращает пустой список, если записи не найдены.
    """
    cur.execute('''
                SELECT *
                FROM dont_touch.parking_releases pr
                WHERE pr.status = %s
                  AND pr.release_date >= %s
                  AND pr.release_date <= %s
                ''', (status, monday_date, friday_date))

    return cur.fetchall()


async def current_spots_releases_by_user(cur, user_id, release_date):
    """
        Асинхронно получает актуальные освобожденные парковочные места пользователя.

        Выполняет SQL-запрос к таблице parking_releases для выборки всех записей,
        которые относятся к указанному пользователю и имеют дату освобождения
        не ранее указанной даты, с определенными статусами.

        Args:
            cur: Курсор базы данных для выполнения SQL-запросов
            user_id (str/UUID): Идентификатор пользователя
            release_date (date): Минимальная дата освобождения для фильтрации

        Returns:
            list[tuple]: Список кортежей с данными освобожденных мест, где каждый кортеж содержит:
                        - spot_id (int): ID парковочного места
                        - status (str): Статус освобождения
                        - release_date (date): Дата освобождения
                        Возвращает пустой список, если записи не найдены.

        Notes:
            - Фильтрует только записи со статусами: 'ACCEPTED', 'PENDING', 'WAITING'
            - Сортирует результаты по дате освобождения в порядке убывания (сначала самые свежие)
            - Используется для отображения актуальных освобожденных мест в статистике пользователя
        """
    cur.execute('''
                SELECT pr.spot_id, pr.status, pr.release_date
                FROM dont_touch.parking_releases pr
                WHERE pr.user_id = %s
                  AND pr.release_date >= %s
                  AND (pr.status = 'ACCEPTED' OR pr.status = 'PENDING' OR pr.status = 'WAITING')
                ORDER BY release_date DESC
                ''', (user_id, release_date,))

    return cur.fetchall()


async def get_tomorrow_accepted_spot(cur, date):
    """
    Асинхронно получает список принятых освобождаемых парковочных мест на указанную дату.

    Выполняет SQL-запрос к таблицам parking_releases и users для выборки информации
    о парковочных местах, которые будут освобождены в указанную дату и имеют статус 'ACCEPTED'.

    Args:
        cur: Курсор базы данных для выполнения SQL-запросов
        date (date): Дата, на которую ищутся освобождаемые места

    Returns:
        list[tuple]: Список кортежей, где каждый кортеж содержит:
                    - spot_id (int): Идентификатор парковочного места
                    - tg_id (int): Telegram ID пользователя, который ЗАБРАЛ место (user_id_took)
                    Возвращает пустой список, если подходящие записи не найдены.

    Notes:
        - Используется для уведомлений пользователей о предстоящем освобождении мест
        - Соединяет таблицы parking_releases и users по user_id_took (пользователь, который взял место)
        - Фильтрует только записи со статусом 'ACCEPTED'
        - Возвращает информацию о пользователях, которые фактически получили освобожденные места
        - Может использоваться для любой даты, несмотря на название 'tomorrow'
    """
    cur.execute("""
                SELECT pr.spot_id, u.tg_id
                FROM dont_touch.parking_releases pr
                         JOIN dont_touch.users u ON pr.user_id_took = u.user_id
                WHERE pr.status = 'ACCEPTED'
                  AND pr.release_date = %s
                """, (date,))

    return cur.fetchall()


async def update_revoke_parking_release(cur, release_id, current_status: ParkingReleaseStatus):
    cur.execute('''
                UPDATE dont_touch.parking_releases
                SET user_id_took = NULL,
                    status       = %s
                WHERE id = %s
                ''', (current_status.name, release_id))


async def find_user_releases_for_revoke(cur, db_user_id, date):
    cur.execute('''
                SELECT prel.id,
                       prel.release_date,
                       prel.status,
                       prel.spot_id
                FROM dont_touch.parking_releases prel
                WHERE prel.user_id = %s
                  AND prel.release_date >= %s
                  AND prel.status = 'PENDING'
                ORDER BY prel.release_date
                ''', (db_user_id, date,))

    return cur.fetchall()

async def find_release_for_confirm_revoke(cur, db_user_id, release_id):
    cur.execute('''
                SELECT prel.id,
                       prel.release_date,
                       prel.status,
                       prel.spot_id
                FROM dont_touch.parking_releases prel
                WHERE prel.user_id = %s
                  AND prel.id = %s
                LIMIT 1
                ''', (db_user_id, release_id,))

    return cur.fetchone()