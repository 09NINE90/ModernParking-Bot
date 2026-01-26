import logging
from enum import Enum
from datetime import datetime

from app.bot.notification.send_log import send_log
from app.config import settings


class LogType(Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARN = 'WARN'
    ERROR = 'ERROR'

    @property
    def message_prefix(self):
        """Возвращает человеко-читаемое название"""
        display_mapping = {
            'DEBUG': '⚙️ DEBUG\n\n',
            'INFO': 'ℹ️ INFO\n\n',
            'WARN': '⚠️ WARN\n\n',
            'ERROR': '❌ ERROR\n\n',
        }
        return display_mapping.get(self.value, self.value)

    @property
    def topic_id(self) -> int:
        """Возвращает человеко-читаемое название"""
        display_mapping = {
            'DEBUG': int(settings.DEBUG_TOPIC_ID),
            'INFO': int(settings.INFO_TOPIC_ID),
            'WARN': int(settings.WARN_TOPIC_ID),
            'ERROR': int(settings.ERROR_TOPIC_ID),
        }
        return display_mapping.get(self.value, self.value)


async def log(log_type: LogType = LogType.ERROR, log_message: str = "", is_sending_log: bool = True) -> None:
    match log_type:
        case LogType.DEBUG:
            logging.debug(log_message)
        case LogType.INFO:
            logging.info(log_message)
        case LogType.WARN:
            logging.warn(log_message)
        case LogType.ERROR:
            logging.error(log_message)

    datetime_now = datetime.now()
    if is_sending_log:
        text = (f"{datetime_now.strftime('%d.%m.%Y %H:%M:%S')}\n"
                f"{log_type.message_prefix}```Message: {log_message}```")
        await send_log(
            topic_id=log_type.topic_id,
            log_message=text
        )


def log_sync(log_type: LogType = LogType.ERROR, log_message: str = "", is_sending_log: bool = True):
    """Синхронная версия логирования"""
    # Локальное логирование
    match log_type:
        case LogType.DEBUG:
            logging.debug(log_message)
        case LogType.INFO:
            logging.info(log_message)
        case LogType.WARN:
            logging.warning(log_message)  # Исправлено: warn -> warning
        case LogType.ERROR:
            logging.error(log_message)

    # Отправка в Telegram (асинхронная, запускаем в фоне)
    if is_sending_log:
        import asyncio
        datetime_now = datetime.now()
        text = (f"{datetime_now.strftime('%d.%m.%Y %H:%M:%S')}\n"
                f"{log_type.message_prefix}```Message: {log_message}```")

        # Запускаем асинхронную отправку в фоне
        asyncio.create_task(_send_log_async(topic_id=log_type.topic_id, log_message=text))


async def _send_log_async(topic_id: int, log_message: str):
    """Внутренняя асинхронная функция отправки"""
    try:
        from app.bot import bot
        from aiogram.enums import ParseMode

        await bot.send_message(
            chat_id=settings.TECH_GROUP_ID,
            message_thread_id=topic_id,
            text=log_message,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logging.error(f"Error sending logs: {e}")
