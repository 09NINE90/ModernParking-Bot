from app.data.migrations.migration_runner import SQLMigrationRunner

def init_database():
    runner = SQLMigrationRunner()
    runner.run_migrations()

def get_db_connection():
    from app.data.migrations import get_connection
    return get_connection()