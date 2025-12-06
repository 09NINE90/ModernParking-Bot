from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения"""

    # Bot
    BOT_TOKEN: str
    GROUP_ID: int
    FEEDBACK_CHANNEL_ID: int
    DELAY_MINUTES_CONFIRM_SPOT: int = 5

    TECH_GROUP_ID: int
    WARN_TOPIC_ID: int
    ERROR_TOPIC_ID: int
    INFO_TOPIC_ID: int
    DEBUG_TOPIC_ID: int
    STATS_TOPIC_ID: int

    # Database
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASSWORD: str
    DB_SCHEMA: str = "public"

    # Logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = "bot.log"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Глобальный экземпляр настроек
settings = Settings()