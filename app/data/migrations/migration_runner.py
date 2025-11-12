import os
import glob
import re
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

        conn = get_connection()
        try:
            for migration in migrations:
                if migration['version'] not in applied_migrations:
                    print(f"Applying migration: {migration['name']}")

                    sql = self.read_sql_file(migration['up_file'])

                    with conn.cursor() as cur:
                        cur.execute(sql)

                    mark_migration_applied(migration['version'], migration['name'])
                    print(f"Migration {migration['name']} applied successfully")

            print("All migrations applied successfully")

        except Exception as e:
            conn.rollback()
            print(f"Migration failed: {e}")
            raise
        finally:
            conn.close()

    def rollback_migration(self, version):
        """Откатывает конкретную миграцию"""
        migrations = self.get_migration_files()
        target_migration = None

        for migration in migrations:
            if migration['version'] == version:
                target_migration = migration
                break

        if not target_migration:
            print(f"Migration version {version} not found")
            return

        if not target_migration['down_file']:
            print(f"Migration {target_migration['name']} doesn't have down file")
            return

        conn = get_connection()
        try:
            print(f"Rolling back migration: {target_migration['name']}")

            sql = self.read_sql_file(target_migration['down_file'])

            with conn.cursor() as cur:
                cur.execute(sql)

            with conn.cursor() as cur:
                cur.execute("DELETE FROM dont_touch.database_migrations WHERE version = %s", (version,))

            conn.commit()
            print(f"Migration {target_migration['name']} rolled back successfully")

        except Exception as e:
            conn.rollback()
            print(f"Rollback failed: {e}")
            raise
        finally:
            conn.close()

    def rollback_last(self):
        """Откатывает последнюю примененную миграцию"""
        applied_migrations = get_applied_migrations()
        if not applied_migrations:
            print("No applied migrations found")
            return

        last_version = max(applied_migrations)
        self.rollback_migration(last_version)

    def status(self):
        """Показывает статус миграций"""
        applied_migrations = get_applied_migrations()
        all_migrations = self.get_migration_files()

        print("Migration Status:")
        print("=================")

        for migration in all_migrations:
            status = "APPLIED" if migration['version'] in applied_migrations else "PENDING"
            print(f"{migration['version']:04d} | {migration['name']:30} | {status}")