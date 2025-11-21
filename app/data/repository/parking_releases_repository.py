from app.data.db_config import DB_SCHEMA
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
    cur.execute(f'''
                SELECT 1
                FROM {DB_SCHEMA}.parking_releases
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
    cur.execute(f'''
                SELECT spot_id
                FROM {DB_SCHEMA}.parking_releases
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
    cur.execute(f'''
                INSERT INTO {DB_SCHEMA}.parking_releases
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
    cur.execute(f'''
                SELECT pr.user_id_took
                FROM {DB_SCHEMA}.parking_releases pr
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
    cur.execute(f'''
                SELECT *
                FROM {DB_SCHEMA}.parking_releases pr
                WHERE pr.status = 'PENDING'
                  AND pr.release_date = %s
                ''', (date,))

    return cur.fetchall()


async def parking_releases_by_week(cur, status, monday_date, friday_date):
    """
    Асинхронно получает записи о возврате парковочных мест за указанную неделю по заданному статусу.

    Выполняет поиск всех записей в таблице parking_releases, соответствующих
    указанному статусу и периоду времени между понедельником и пятницей.

    Параметры:
        cur: курсор базы данных для выполнения SQL-запросов
        status: статус записей о возврате для фильтрации (например, 'ACCEPTED', 'NOT_FOUND')
        monday_date: дата понедельника (начало периода, включительно)
        friday_date: дата пятницы (конец периода, включительно)

    Возвращает:
        list: список кортежей со всеми полями записей о возвратах, удовлетворяющих условиям

    Особенности:
        - Возвращает все поля таблицы parking_releases (*)
        - Фильтрация происходит по статусу и диапазону дат (включительно)
        - Используется для получения статистики возвратов за конкретную неделю
        - Функция асинхронная, требует await при вызове
    """
    cur.execute(f'''
                SELECT *
                FROM {DB_SCHEMA}.parking_releases pr
                WHERE pr.status = %s
                  AND pr.release_date >= %s
                  AND pr.release_date <= %s
                ''', (status, monday_date, friday_date))

    return cur.fetchall()


async def current_spots_releases_by_user(cur, user_id, release_date):
    """
    Асинхронно получает актуальные освобожденные парковочные места пользователя.

    Выполняет поиск активных и ожидающих запросов на освобождение парковочных мест
    для указанного пользователя, начиная с заданной даты.

    Параметры:
        cur: курсор базы данных для выполнения SQL-запросов
        user_id: UUID идентификатор пользователя в базе данных
        release_date: минимальная дата освобождения для фильтрации (включительно)

    Возвращает:
        list: список кортежей с данными освобожденных мест, где каждый кортеж содержит:
            - spot_id: идентификатор парковочного места
            - status: статус освобождения (f'ACCEPTED', 'PENDING' или 'WAITING')
            - release_date: дата освобождения места

    Особенности:
        - Фильтрует записи со статусами 'ACCEPTED', 'PENDING' и 'WAITING'
        - Результаты сортируются по дате освобождения в порядке убывания (сначала новые)
        - Используется для отображения актуальных освобожденных мест в статистике пользователя
        - Функция асинхронная, требует await при вызове
    """
    cur.execute(f'''
                SELECT pr.spot_id, pr.status, pr.release_date
                FROM {DB_SCHEMA}.parking_releases pr
                WHERE pr.user_id = %s
                  AND pr.release_date >= %s
                  AND (pr.status = 'ACCEPTED' OR pr.status = 'PENDING' OR pr.status = 'WAITING')
                ORDER BY release_date DESC
                ''', (user_id, release_date,))

    return cur.fetchall()


async def get_tomorrow_accepted_spot(cur, date):
    """
    Асинхронно получает список принятых освобождаемых парковочных мест на указанную дату.

    Выполняет поиск информации о парковочных местах, которые будут освобождены
    в указанную дату и имеют статус 'ACCEPTED', с данными пользователей, получивших эти места.

    Параметры:
        cur: курсор базы данных для выполнения SQL-запросов
        date: дата, на которую ищутся освобождаемые места

    Возвращает:
        list: список кортежей, где каждый кортеж содержит:
            - spot_id: идентификатор парковочного места
            - tg_id: Telegram ID пользователя, который забрал место (user_id_took)

    Особенности:
        - JOIN с таблицей users для получения Telegram ID пользователей
        - Фильтрует только записи со статусом 'ACCEPTED'
        - Возвращает информацию о пользователях, которые фактически получили освобожденные места
        - Используется для уведомлений пользователей о предстоящем освобождении мест
        - Функция асинхронная, требует await при вызове
    """
    cur.execute("""
                SELECT prel.spot_id, u.tg_id, u.user_id, prel.id, prel.release_date, prq.id
                FROM {DB_SCHEMA}.parking_releases prel
                         JOIN {DB_SCHEMA}.users u ON prel.user_id_took = u.user_id
                         JOIN {DB_SCHEMA}.parking_requests prq
                              ON prq.user_id = prel.user_id_took 
                                  AND prq.request_date = prel.release_date
                WHERE prel.status = 'ACCEPTED'
                  AND prel.release_date = %s
                """, (date,))

    return cur.fetchall()


async def update_revoke_parking_release(cur, release_id, current_status: ParkingReleaseStatus):
    """
        Асинхронно обновляет запрос на освобождение места при отзыве.

        Сбрасывает привязку к пользователю и обновляет статус запроса на освобождение
        парковочного места при отзыве заявки.

        Параметры:
            cur: курсор базы данных для выполнения SQL-запросов
            release_id: UUID идентификатор запроса на освобождение места
            current_status: новый статус запроса (enum ParkingReleaseStatus)

        Возвращает:
            None: функция выполняет UPDATE запрос и не возвращает данные

        Особенности:
            - Сбрасывает user_id_took в NULL (убирает привязку к пользователю)
            - Обновляет статус на указанное значение
            - Использует current_status.name для получения строкового значения enum
            - Обновляет только одну запись по идентификатору release_id
            - Используется в процессе отзыва заявки на освобождение места
            - Функция асинхронная, требует await при вызове
    """
    cur.execute(f'''
                UPDATE {DB_SCHEMA}.parking_releases
                SET user_id_took = NULL,
                    status       = %s
                WHERE id = %s
                ''', (current_status.name, release_id))


async def find_user_releases_for_revoke(cur, db_user_id, date):
    """
        Асинхронно находит запросы на освобождение мест пользователя для возможного отзыва.

        Выполняет поиск ожидающих запросов на освобождение парковочных мест,
        начиная с указанной даты.

        Параметры:
            cur: курсор базы данных для выполнения SQL-запросов
            db_user_id: UUID идентификатор пользователя в базе данных
            date: дата, начиная с которой осуществляется поиск запросов (включительно)

        Возвращает:
            list: список кортежей с данными запросов на освобождение, где каждый кортеж содержит:
                - id: идентификатор запроса на освобождение
                - release_date: дата освобождения места
                - status: статус запроса (всегда 'PENDING')
                - spot_id: идентификатор освобождаемого места парковки

        Особенности:
            - Ищет только записи со статусом 'PENDING'
            - Результаты сортируются по дате освобождения в возрастающем порядке
            - Используется для функциональности отзыва запросов на освобождение мест
            - Функция асинхронная, требует await при вызове
    """
    cur.execute(f'''
                SELECT prel.id,
                       prel.release_date,
                       prel.status,
                       prel.spot_id
                FROM {DB_SCHEMA}.parking_releases prel
                WHERE prel.user_id = %s
                  AND prel.release_date >= %s
                  AND prel.status = 'PENDING'
                ORDER BY prel.release_date
                ''', (db_user_id, date,))

    return cur.fetchall()


async def find_release_for_confirm_revoke(cur, db_user_id, release_id):
    """
        Асинхронно находит запрос на освобождение места для подтверждения отзыва.

        Выполняет поиск конкретного запроса на освобождение парковочного места
        по ID пользователя и ID запроса на освобождение.

        Параметры:
            cur: курсор базы данных для выполнения SQL-запросов
            db_user_id: UUID идентификатор пользователя в базе данных
            release_id: UUID идентификатор запроса на освобождение места

        Возвращает:
            tuple или None: кортеж с данными запроса на освобождение в формате:
                - id: идентификатор запроса на освобождение
                - release_date: дата освобождения места
                - status: статус запроса
                - spot_id: идентификатор освобождаемого места парковки
            или None, если запрос не найден

        Особенности:
            - Ищет конкретный запрос по комбинации user_id и release_id
            - Ограничивает результат одной записью (LIMIT 1)
            - Используется для подтверждения отзыва запроса на освобождение места
            - Функция асинхронная, требует await при вызове
    """
    cur.execute(f'''
                SELECT prel.id,
                       prel.release_date,
                       prel.status,
                       prel.spot_id
                FROM {DB_SCHEMA}.parking_releases prel
                WHERE prel.user_id = %s
                  AND prel.id = %s
                LIMIT 1
                ''', (db_user_id, release_id,))

    return cur.fetchone()


async def update_parking_releases(cur, user_id, release_id, current_status: ParkingReleaseStatus):
    """
    Назначает парковочное место конкретному пользователю.

    Обновляет запись об освобожденном месте, указывая пользователя, который получил
    это место в свое распоряжение.

    Параметры:
        cur: курсор базы данных для выполнения SQL-запросов
        user_id: UUID пользователя, который получает место
        release_id: UUID записи в таблице parking_releases

    Логика:
        - Устанавливает user_id_took = указанному пользователю
        - Превращает свободное место в занятое конкретным пользователем

    Особенности:
        - Критическая операция в процессе распределения мест
        - После выполнения место перестает быть свободным (user_id_took IS NULL → user_id_took = user_id)
        - Асинхронная функция, требует await при вызове
    """
    cur.execute(f'''
                UPDATE {DB_SCHEMA}.parking_releases
                SET user_id_took = %s,
                    status       = %s
                WHERE id = %s
                ''', (user_id, current_status.name, release_id))


async def get_release_owner(cur, release_id):
    """
       Получает информацию о пользователе, который освободил парковочное место.

       Находит владельца (инициатора освобождения) парковочного места по идентификатору
       записи в таблице parking_releases.

       Параметры:
           cur: курсор базы данных для выполнения SQL-запросов
           release_id: UUID записи в таблице parking_releases

       Возвращает:
           dict или None:
               - Словарь с полями 'user_id' (UUID владельца) и 'tg_id' (Telegram ID владельца)
               - None, если запись с указанным release_id не найдена

       Логика:
           - Ищет запись в parking_releases по первичному ключу (id)
           - Присоединяет таблицу users чтобы получить Telegram ID владельца
           - Возвращает идентификаторы как внутренние (user_id), так и внешние (tg_id)

       Особенности:
           - Используется для уведомления первоначального владельца о событиях с его местом
           - Возвращает именно того, кто ОСВОБОДИЛ место (user_id), а не того, кто его занял (user_id_took)
           - Асинхронная функция, требует await при вызове
           - Полезно для систем уведомлений и аудита действий
       """
    cur.execute(f'''
                SELECT pr.user_id, u.tg_id
                FROM {DB_SCHEMA}.parking_releases pr
                         JOIN {DB_SCHEMA}.users u ON pr.user_id = u.user_id
                WHERE pr.id = %s
                ''', (release_id,))

    return cur.fetchone()


async def get_free_spots(cur, distribution_date):
    """
        Получает список свободных парковочных мест на указанную дату.

        Выполняет поиск всех освобожденных парковочных мест на конкретную дату,
        которые еще не были заняты другими пользователями.

        Параметры:
            cur: курсор базы данных для выполнения SQL-запросов
            distribution_date: дата, на которую запрашиваются свободные места

        Возвращает:
            list: список словарей, где каждый словарь содержит:
                - 'id': UUID записи в таблице parking_releases
                - 'spot_id': идентификатор парковочного места

        Логика:
            - Ищет записи в parking_releases где release_date совпадает с указанной датой
            - Фильтрует только свободные места (user_id_took IS NULL)
            - Сортирует результаты по времени создания (created_at) в порядке возрастания
              для обеспечения детерминированного порядка распределения

        Особенности:
            - Возвращает именно свободные места (никем не занятые)
            - ORDER BY created_at ASC обеспечивает fair distribution - первыми
              распределяются места, которые были освобождены раньше
            - Асинхронная функция, требует await при вызове
            - Используется в процессах автоматического распределения мест
        """
    cur.execute(f'''
                SELECT id, spot_id
                FROM {DB_SCHEMA}.parking_releases
                WHERE release_date = %s
                  AND status = 'PENDING'
                ORDER BY created_at ASC
                ''', (distribution_date,))
    return cur.fetchall()
