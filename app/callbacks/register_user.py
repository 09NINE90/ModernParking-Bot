import logging

import psycopg2

from app.db_config import DATABASE_CONFIG

async def register_user(user):
    """Регистрация пользователя в системе"""
    conn = None
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        # Сначала проверяем, существует ли пользователь
        cursor.execute('SELECT user_id FROM dont_touch.users WHERE tg_id = %s', (user.id,))
        existing_user = cursor.fetchone()

        if not existing_user:
            # Если пользователя нет, создаем нового
            cursor.execute('''
                           INSERT INTO dont_touch.users (user_id, tg_id)
                           VALUES (gen_random_uuid(), %s)
                           ''', (user.id,))
            conn.commit()
            logging.info(f"New user registered: {user.id}")
        else:
            logging.info(f"User already exists: {user.id}")

    except Exception as e:
        logging.error(f"Error registering user: {e}")
        # Если все еще есть ошибка, используем простую вставку без ON CONFLICT
        try:
            cursor.execute('''
                           INSERT INTO dont_touch.users (user_id, tg_id)
                           VALUES (gen_random_uuid(), %s)
                           ''', (user.id,))
            conn.commit()
        except:
            pass  # Игнорируем ошибку дубликата
    finally:
        if conn:
            conn.close()