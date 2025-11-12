import logging

from app.data.init_db import get_db_connection

# Регистрация пользователя в системе
async def register_user(user):
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
                logging.info(f"New user registered: {user.id}")
                return True
            else:
                logging.info(f"User already exists: {user.id}")
                return False

    except Exception as e:
        logging.error(f"Error registering user {user.id}: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()
