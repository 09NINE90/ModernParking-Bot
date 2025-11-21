import os
import glob
import re

from app.data.db_config import DB_SCHEMA
from app.data.migrations import (
    get_connection,
    create_migrations_table,
    get_applied_migrations,
    mark_migration_applied
)


class SQLMigrationRunner:
    def __init__(self):
        self.migrations_path = os.path.join(os.path.dirname(__file__), 'versions')

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
        create_migrations_table()
        applied_migrations = get_applied_migrations()
        migrations = self.get_migration_files()

        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    for migration in migrations:
                        if migration['version'] not in applied_migrations:
                            print(f"Applying migration: {migration['name']}")

                            sql = self.read_sql_file(migration['up_file'])
                            sql = sql.replace("DEFAULT_SCHEMA", DB_SCHEMA)
                            print(f"sql = {sql}")
                            cur.execute(sql)

                            mark_migration_applied(migration['version'], migration['name'])
                            print(f"Migration {migration['name']} applied successfully")

                    print("All migrations applied successfully")
                    print(self.status())

        except Exception as e:
            conn.rollback()
            print(f"Migration failed: {e}")
            raise

    def status(self):
        """Показывает статус миграций"""
        applied_migrations = get_applied_migrations()
        all_migrations = self.get_migration_files()

        print("Migration Status:")
        print("=================")

        for migration in all_migrations:
            status = "APPLIED" if migration['version'] in applied_migrations else "PENDING"
            print(f"{migration['version']:04d} | {migration['name']:30} | {status}")