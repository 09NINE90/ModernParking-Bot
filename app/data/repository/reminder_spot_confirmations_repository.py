from app.data.db_config import DB_SCHEMA


async def insert_row_of_reminder_spot_confirmations(cur, user_id, release_id, request_id):
    cur.execute(f"""
                INSERT INTO {DB_SCHEMA}.reminder_spot_confirmations (user_id, release_id, request_id)
                VALUES (%s, %s, %s)
                """, (user_id, release_id, request_id,))

async def find_reminder_spot_confirmations_by_user(cur, user_id):
    cur.execute(f"""
                SELECT u.user_id, u.tg_id, prl.spot_id, prl.release_date, sc.release_id, sc.request_id
                FROM {DB_SCHEMA}.reminder_spot_confirmations sc
                         JOIN {DB_SCHEMA}.users u ON u.user_id = sc.user_id
                         JOIN {DB_SCHEMA}.parking_releases prl ON prl.id = sc.release_id
                WHERE sc.user_id = %s
                  AND sc.is_active = TRUE
                ORDER BY sc.created_at DESC
                LIMIT 1
                """, (user_id,))

    return cur.fetchone()

async def deactivate_reminder_spot_confirmations_by_user(cur, user_id):
    cur.execute(f"""
                UPDATE {DB_SCHEMA}.reminder_spot_confirmations
                SET is_active  = FALSE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id IN (SELECT user_id
                                  FROM {DB_SCHEMA}.users
                                  WHERE user_id = %s)
                  AND is_active = TRUE
                """, (user_id,))