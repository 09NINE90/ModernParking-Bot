async def get_dates_with_availability(cur):
    """
        Получает список дат, на которые есть доступные парковочные места и ожидающие запросы.

        Выполняет поиск дат, где одновременно выполняются два условия:
        1. Есть освобожденные парковочные места, которые еще не заняты
        2. Есть pending-запросы на парковку на эти же даты

        Параметры:
            cur: курсор базы данных для выполнения SQL-запросов

        Возвращает:
            list: список объектов datetime.date - даты, когда возможна автоматическая
                  выдача парковочных мест (есть и свободные места, и запросы на них)

        Логика:
            - Основной запрос ищет даты из parking_releases где user_id_took IS NULL
              (места свободны)
            - Подзапрос EXISTS проверяет, что на эти же даты есть запросы со статусом 'PENDING'
            - DISTINCT гарантирует уникальность дат в результате

        Особенности:
            - Функция используется для поиска дат, когда система может автоматически
              распределить свободные места среди ожидающих пользователей
            - Возвращает только даты, где есть и предложение (свободные места), и спрос (запросы)
            - Асинхронная функция, требует await при вызове
        """
    cur.execute('''
                SELECT DISTINCT pr.release_date
                FROM dont_touch.parking_releases pr
                WHERE pr.status = 'PENDING'
                  AND EXISTS (SELECT 1
                              FROM dont_touch.parking_requests prq
                              WHERE prq.request_date = pr.release_date
                                AND prq.status = 'PENDING')
                ''')

    return [row[0] for row in cur.fetchall()]


async def get_candidates(cur, distribution_date, free_spots):
    """
        Получает список кандидатов для распределения свободных мест на указанную дату.

        Выбирает пользователей с pending-запросами на парковку, упорядоченных по рейтингу,
        для последующего распределения среди них доступных свободных мест.

        Параметры:
            cur: курсор базы данных для выполнения SQL-запросов
            distribution_date: дата, на которую распределяются места
            free_spots: список свободных мест (используется для определения лимита кандидатов)

        Возвращает:
            list: список словарей, где каждый словарь содержит:
                - 'request_id': UUID запроса на парковку
                - 'user_id': UUID пользователя
                - 'rating': рейтинг пользователя (числовое значение)
                - 'tg_id': идентификатор пользователя в Telegram

        Логика:
            - Выбирает pending-запросы на указанную дату
            - Присоединяет данные пользователей для получения рейтинга и tg_id
            - Сортирует по рейтингу в порядке возрастания (низший рейтинг первый)
            - Ограничивает количество кандидатов количеством свободных мест

        Особенности:
            - ORDER BY u.rating ASC - приоритет отдается пользователям с НИЗШИМ рейтингом
              (вероятно, система справедливого распределения, где меньше получившие)
            - LIMIT %s - количество кандидатов равно количеству свободных мест
            - Статус 'PENDING' - рассматриваются только активные, необработанные запросы
            - Асинхронная функция, требует await при вызове
        """
    cur.execute('''
                SELECT prq.id as request_id, prq.user_id, u.rating, u.tg_id
                FROM dont_touch.parking_requests prq
                         JOIN dont_touch.users u ON prq.user_id = u.user_id
                WHERE prq.request_date = %s
                  AND prq.status = 'PENDING'
                  AND NOT EXISTS (SELECT 1
                                  FROM dont_touch.parking_releases prl
                                  WHERE prl.user_id = prq.user_id
                                    AND prl.release_date = %s
                                    AND prl.status = 'PENDING')
                ORDER BY u.rating ASC
                LIMIT %s
                ''', (distribution_date, distribution_date, len(free_spots)))

    return cur.fetchall()
