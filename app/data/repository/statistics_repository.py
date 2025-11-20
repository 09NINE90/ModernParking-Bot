
async def get_parking_transfers_by_date(cur, date):
    """
    Асинхронно получает информацию о трансферах парковочных мест за указанную дату.

    Выполняет поиск информации о парковочных местах, которые были переданы
    от одного пользователя другому в указанную дату со статусом 'ACCEPTED'.

    Параметры:
        cur: курсор базы данных для выполнения SQL-запросов
        date: дата, за которую нужно получить информацию о трансферах

    Возвращает:
        list: список кортежей с информацией о трансферах, где каждый кортеж содержит:
            - spot_id: идентификатор парковочного места
            - recipient_tg_id: Telegram ID пользователя, получившего место
            - owner_tg_id: Telegram ID пользователя, отдавшего место

    Особенности:
        - JOIN с таблицей users дважды (для владельца и получателя места)
        - Фильтрует записи с заполненным user_id_took и статусом 'ACCEPTED'
        - Возвращает только успешные трансферы мест между пользователями
        - Используется для анализа передачи парковочных мест
        - Функция асинхронная, требует await при вызове
    """
    cur.execute('''
                SELECT pr.spot_id,
                       recipient.tg_id AS recipient_tg_id,
                       owner.tg_id     AS owner_tg_id
                FROM dont_touch.parking_releases pr
                         JOIN dont_touch.users owner ON pr.user_id = owner.user_id
                         JOIN dont_touch.users recipient ON pr.user_id_took = recipient.user_id
                WHERE pr.release_date = %s
                  AND pr.user_id_took IS NOT NULL
                    AND pr.status = 'ACCEPTED';
                ''', (date,))

    return cur.fetchall()


async def get_parking_transfers_by_week(cur, monday_date, friday_date):
    """
    Асинхронно получает информацию о передачах парковочных мест между пользователями за указанную неделю.

    Выполняет поиск информации об успешных передачах парковочных мест от одного пользователя
    другому в течение периода с понедельника по пятницу включительно.

    Параметры:
        cur: курсор базы данных для выполнения SQL-запросов
        monday_date: дата понедельника (начало периода, включительно)
        friday_date: дата пятницы (конец периода, включительно)

    Возвращает:
        list: список кортежей с информацией о трансферах, где каждый кортеж содержит:
            - spot_id: идентификатор парковочного места
            - recipient_tg_id: Telegram ID пользователя, получившего место
            - owner_tg_id: Telegram ID пользователя, передавшего место

    Особенности:
        - JOIN с таблицей users дважды (для владельца и получателя места)
        - Фильтрует записи с заполненным user_id_took и статусом 'ACCEPTED'
        - Охватывает диапазон дат от понедельника до пятницы включительно
        - Возвращает все успешные трансферы мест за указанную неделю
        - Используется для недельной статистики передачи парковочных мест
        - Функция асинхронная, требует await при вызове
    """
    cur.execute('''
                SELECT pr.spot_id,
                       recipient.tg_id AS recipient_tg_id,
                       owner.tg_id     AS owner_tg_id
                FROM dont_touch.parking_releases pr
                         JOIN dont_touch.users owner ON pr.user_id = owner.user_id
                         JOIN dont_touch.users recipient ON pr.user_id_took = recipient.user_id
                WHERE pr.release_date >= %s
                  AND pr.release_date <= %s
                  AND pr.user_id_took IS NOT NULL
                  AND pr.status = 'ACCEPTED';
                ''', (monday_date, friday_date,))

    return cur.fetchall()