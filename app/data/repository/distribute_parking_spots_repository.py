# Получить даты на которые есть запросы
async def get_dates_with_availability(cur):
    cur.execute('''
                SELECT DISTINCT pr.release_date
                FROM dont_touch.parking_releases pr
                WHERE pr.user_id_took IS NULL
                  AND EXISTS (SELECT 1
                              FROM dont_touch.parking_requests prq
                              WHERE prq.request_date = pr.release_date
                                AND prq.status = 'PENDING')
                ''')

    return [row[0] for row in cur.fetchall()]

# Получить свободные места по дате
async def get_free_spots(cur, distribution_date):
    cur.execute('''
                SELECT id, spot_id
                FROM dont_touch.parking_releases
                WHERE release_date = %s
                  AND user_id_took IS NULL
                ORDER BY created_at ASC
                ''', (distribution_date,))
    return cur.fetchall()

# Получить кандидатов на места по дате
async def get_candidates(cur, distribution_date, free_spots):
    cur.execute('''
                SELECT prq.id as request_id, prq.user_id, u.rating, u.tg_id
                FROM dont_touch.parking_requests prq
                         JOIN dont_touch.users u ON prq.user_id = u.user_id
                WHERE prq.request_date = %s
                  AND prq.status = 'PENDING'
                ORDER BY u.rating ASC
                LIMIT %s
                ''', (distribution_date, len(free_spots)))
    return cur.fetchall()

# Получить пользователя, который освободил место
async def get_release_owner(cur, release_id):
    cur.execute('''
                SELECT pr.user_id, u.tg_id
                FROM dont_touch.parking_releases pr
                         JOIN dont_touch.users u ON pr.user_id = u.user_id
                WHERE pr.id = %s
                ''', (release_id,))
    return cur.fetchone()

# Назначаем место пользователю
async def update_parking_releases(cur, user_id, release_id):
    cur.execute('''
                UPDATE dont_touch.parking_releases
                SET user_id_took = %s
                WHERE id = %s
                ''', (user_id, release_id))


# Обновляем статус запроса
async def update_parking_requests(cur, request_id):
    cur.execute('''
                UPDATE dont_touch.parking_requests
                SET status       = 'ACCEPT',
                    processed_at = CURRENT_TIMESTAMP
                WHERE id = %s
                ''', (request_id,))


# Увеличиваем рейтинг пользователя
async def update_users(cur, user_id):
    cur.execute('''
                UPDATE dont_touch.users
                SET rating = rating + 1
                WHERE user_id = %s
                ''', (user_id,))