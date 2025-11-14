
async def get_parking_transfers_by_date(cur, date):
    """
        Получает информацию о трансферах парковочных мест за указанную дату.

        Выполняет SQL-запрос к базе данных для получения списка парковочных мест,
        которые были переданы от одного пользователя другому в указанную дату.

        Args:
            cur: Курсор базы данных для выполнения запроса
            date (datetime.date): Дата, за которую нужно получить трансферы

        Returns:
            list: Список кортежей с информацией о трансферах, где каждый кортеж содержит:
                - spot_id (int): ID парковочного места
                - recipient_tg_id (int): Telegram ID пользователя, получившего место
                - owner_tg_id (int): Telegram ID пользователя, отдавшего место
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

        Выполняет SQL-запрос к базе данных для получения списка успешных передач парковочных мест
        от одного пользователя другому в течение периода с понедельника по пятницу.

        Args:
            cur: Курсор базы данных для выполнения SQL-запросов
            monday_date: Дата понедельника (начало периода поиска)
            friday_date: Дата пятницы (конец периода поиска)

        Returns:
            list[tuple]: Список кортежей с информацией о трансферах, где каждый кортеж содержит:
                - spot_id (int): ID парковочного места
                - recipient_tg_id (int): Telegram ID пользователя, получившего место
                - owner_tg_id (int): Telegram ID пользователя, передавшего место
            Возвращает пустой список, если передачи не найдены.
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