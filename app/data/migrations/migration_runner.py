import os
import glob
import re
import psycopg2
from app.config import settings
from app.data.database import get_db_config  # Импортируем безопасно


class SQLMigrationRunner:
    def __init__(self):
        self.migrations_path = os.path.join(os.path.dirname(__file__), 'versions')
        self.db_config = get_db_config()  # Получаем конфиг один раз

    def get_connection(self):
        """Создает соединение с БД"""
        return psycopg2.connect(**self.db_config)

    def create_migrations_table(self, conn):
        """Создает таблицу миграций"""
        with conn.cursor() as cur:
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {settings.DB_SCHEMA}")
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {settings.DB_SCHEMA}.database_migrations
                (
                    id         SERIAL PRIMARY KEY,
                    version    INTEGER UNIQUE NOT NULL,
                    name       VARCHAR(255)   NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

    def get_applied_migrations(self, conn):
        """Получает список примененных миграций"""
        with conn.cursor() as cur:
            cur.execute(f"SELECT version FROM {settings.DB_SCHEMA}.database_migrations ORDER BY version")
            return {row[0] for row in cur.fetchall()}

    def mark_migration_applied(self, conn, version: int, name: str):
        """Отмечает миграцию как примененную"""
        with conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {settings.DB_SCHEMA}.database_migrations (version, name) VALUES (%s, %s)",
                (version, name)
            )
            conn.commit()

    def get_migration_files(self):
        """Возвращает отсортированный список файлов миграций"""
        up_files = glob.glob(os.path.join(self.migrations_path, "*_*.up.sql"))

        up_files.sort(key=lambda x: int(re.search(r'(\d+)_', os.path.basename(x)).group(1)))

        migrations = []
        for up_file in up_files:
            version = int(re.search(r'(\d+)_', os.path.basename(up_file)).group(1))
            name = os.path.basename(up_file).replace('.up.sql', '')
            down_file = up_file.replace('.up.sql', '.down.sql')

            migrations.append({
                'version': version,
                'name': name,
                'up_file': up_file,
                'down_file': down_file if os.path.exists(down_file) else None
            })

        return migrations

    def read_sql_file(self, file_path):
        """Читает SQL файл"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def run_migrations(self):
        """Запускает все непримененные миграции"""
        conn = self.get_connection()
        try:
            self.create_migrations_table(conn)
            applied_migrations = self.get_applied_migrations(conn)
            migrations = self.get_migration_files()

            with conn.cursor() as cur:
                for migration in migrations:
                    if migration['version'] not in applied_migrations:
                        print(f"Applying migration: {migration['name']}")

                        sql = self.read_sql_file(migration['up_file'])
                        sql = sql.replace("DEFAULT_SCHEMA", settings.DB_SCHEMA)
                        print(f"sql = {sql}")
                        cur.execute(sql)

                        self.mark_migration_applied(conn, migration['version'], migration['name'])
                        print(f"Migration {migration['name']} applied successfully")

                print("All migrations applied successfully")
                print(self.status())

        except Exception as e:
            conn.rollback()
            print(f"Migration failed: {e}")
            raise
        finally:
            conn.close()

    def status(self):
        """Показывает статус миграций"""
        conn = self.get_connection()
        try:
            applied_migrations = self.get_applied_migrations(conn)
            all_migrations = self.get_migration_files()

            print("Migration Status:")
            print("=================")

            for migration in all_migrations:
                status = "APPLIED" if migration['version'] in applied_migrations else "PENDING"
                print(f"{migration['version']:04d} | {migration['name']:30} | {status}")
        finally:
            conn.close()