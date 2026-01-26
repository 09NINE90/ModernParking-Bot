import psycopg2

def get_connection(db_config: dict):
    """Создает соединение с переданной конфигурацией"""
    return psycopg2.connect(**db_config)

def create_migrations_table(conn, db_schema: str):
    """Создает таблицу миграций"""
    with conn.cursor() as cur:
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {db_schema}")
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {db_schema}.database_migrations
            (
                id         SERIAL PRIMARY KEY,
                version    INTEGER UNIQUE NOT NULL,
                name       VARCHAR(255)   NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

def get_applied_migrations(conn, db_schema: str):
    """Получает список примененных миграций"""
    with conn.cursor() as cur:
        cur.execute(f"SELECT version FROM {db_schema}.database_migrations ORDER BY version")
        return {row[0] for row in cur.fetchall()}

def mark_migration_applied(conn, db_schema: str, version: int, name: str):
    """Отмечает миграцию как примененную"""
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO {db_schema}.database_migrations (version, name) VALUES (%s, %s)",
            (version, name)
        )
        conn.commit()

def mark_migration_rolled_back(conn, db_schema: str, version: int):
    """Отмечает миграцию как откаченную"""
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM {db_schema}.database_migrations WHERE version = %s", (version,))
        conn.commit()

__all__ = [
    'get_connection',
    'create_migrations_table',
    'get_applied_migrations',
    'mark_migration_applied',
    'mark_migration_rolled_back',
]