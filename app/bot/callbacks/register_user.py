import logging

from app.data.init_db import get_db_connection

async def register_user(user):
    """
        Регистрирует нового пользователя в системе.

        Проверяет существование пользователя в базе данных и при отсутствии создает новую запись.

        Параметры:
            user: объект пользователя Telegram с идентификатором

        Возвращает:
            bool: True если пользователь зарегистрирован, False если уже существует или ошибка
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                'SELECT user_id FROM dont_touch.users WHERE tg_id = %s',
                (user.id,)
            )
            existing_user = cur.fetchone()

            if not existing_user:
                cur.execute(
                    'INSERT INTO dont_touch.users (user_id, tg_id) VALUES (gen_random_uuid(), %s)',
                    (user.id,)
                )
                conn.commit()
                logging.debug(f"New user registered: {user.id}")
                return True
            else:
                logging.debug(f"User already exists: {user.id}")
                return False

    except Exception as e:
        logging.error(f"Error registering user {user.id}: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()
