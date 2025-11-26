from app.data.db_config import DB_SCHEMA
from app.data.models.schedule_dto import ScheduleDto


async def add_spot_requests_schedule(cur, user_id, day_numbers):
    cur.execute(f"""INSERT INTO {DB_SCHEMA}.spot_requests_schedule (user_id, day_numbers)
                       VALUES (%s, %s)
                       ON CONFLICT (user_id, day_numbers) 
                       DO NOTHING
                       RETURNING id
                    """, (user_id, day_numbers))

    result = cur.fetchone()
    if result:
        return result
    else:
        return None


async def get_spot_requests_schedule_by_user(cur, user_id):
    cur.execute(f"""SELECT day_numbers FROM {DB_SCHEMA}.spot_requests_schedule 
                    WHERE user_id = %s
                """, (user_id,))

    rows = cur.fetchall()
    if rows:
        return [row[0] for row in rows]
    else:
        return None


async def get_spot_requests_schedule_by_user_with_id(cur, user_id) -> list[ScheduleDto] | None:
    cur.execute(f"""SELECT id, day_numbers FROM {DB_SCHEMA}.spot_requests_schedule 
                    WHERE user_id = %s
                """, (user_id,))

    rows = cur.fetchall()
    if rows:
        return [ScheduleDto(id=row[0], day_numbers=row[1]) for row in rows]
    else:
        return None


async def get_spot_requests_schedule_by_id(cur, schedule_id: str) -> ScheduleDto | None:
    """Получает полную запись расписания по его ID"""
    cur.execute(f"""SELECT id, day_numbers FROM {DB_SCHEMA}.spot_requests_schedule 
                    WHERE id = %s
                """, (schedule_id,))

    row = cur.fetchone()
    if row:
        return ScheduleDto(id=row[0], day_numbers=row[1])
    else:
        return None


async def delete_spot_requests_schedule_by_id(cur, schedule_id: str) -> bool:
    """Удаляет запись расписания по его ID"""
    cur.execute(f"""DELETE FROM {DB_SCHEMA}.spot_requests_schedule 
                    WHERE id = %s
                """, (schedule_id,))

    return cur.rowcount > 0

async def get_user_schedules_with_tg_id(cur):
    cur.execute(f"""
                    SELECT u.tg_id,
                       JSON_AGG(
                               JSON_BUILD_OBJECT(
                                       'id', srs.id,
                                       'day_numbers', srs.day_numbers
                               )
                       ) as schedules
                FROM {DB_SCHEMA}.spot_requests_schedule srs
                         JOIN {DB_SCHEMA}.users u ON u.user_id = srs.user_id
                GROUP BY u.tg_id;
                """)
    rows = cur.fetchall()
    if not rows:
        return None

    result = {}
    for row in rows:
        tg_id = row[0]
        schedules_data = row[1]

        schedules = [ScheduleDto(id=sched['id'], day_numbers=sched['day_numbers'])
                     for sched in schedules_data]

        result[tg_id] = schedules

    return result