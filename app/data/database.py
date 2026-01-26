import psycopg2
import logging

from contextlib import contextmanager
from app.config.settings import settings

logger = logging.getLogger(__name__)


def get_db_config():
    """Получение конфигурации БД"""
    return {
        "dbname": settings.DB_NAME,
        "host": settings.DB_HOST,
        "port": settings.DB_PORT,
        "user": settings.DB_USER,
        "password": settings.DB_PASSWORD,
    }


@contextmanager
def get_db_connection():
    """Контекстный менеджер для соединения с БД"""
    conn = None
    try:
        conn = psycopg2.connect(**get_db_config())
        logger.debug("Database connection opened")
        yield conn
        conn.commit()  # Автоматический коммит при успешном завершении
        logger.debug("Database transaction committed")
    except Exception as e:
        if conn:
            conn.rollback()
            logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")


@contextmanager
def get_db_cursor():
    """Контекстный менеджер для курсора"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            yield cur


def init_database():
    """Инициализация базы данных"""
    try:
        # Проверяем соединение
        with get_db_connection():
            logger.info("Database connection test successful")

        from .migrations.migration_runner import SQLMigrationRunner
        runner = SQLMigrationRunner()
        runner.run_migrations()

        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise