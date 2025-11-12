import psycopg2

from app.data.db_config import DATABASE_CONFIG

def get_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


def create_migrations_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS dont_touch")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS dont_touch.database_migrations
                (
                    id         SERIAL PRIMARY KEY,
                    version    INTEGER UNIQUE NOT NULL,
                    name       VARCHAR(255)   NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()


def get_applied_migrations():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version FROM dont_touch.database_migrations ORDER BY version")
            return {row[0] for row in cur.fetchall()}


def mark_migration_applied(version, name):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO dont_touch.database_migrations (version, name) VALUES (%s, %s)",
                (version, name)
            )
            conn.commit()

def mark_migration_rolled_back(version):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM dont_touch.database_migrations WHERE version = %s", (version,))
            conn.commit()
__all__ = [
    'get_connection',
    'create_migrations_table',
    'get_applied_migrations',
    'mark_migration_applied',
    'mark_migration_rolled_back',
    'DATABASE_CONFIG'
]