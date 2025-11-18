import logging
from functools import wraps

from app.bot.config import bot
from app.bot.constants.log_types import LogNotification
from app.bot.notification.log_notification import send_log_notification
from app.log_text import CHAT_ACCESS_ERROR


def chat_access_required(func):
    """Декоратор для проверки доступа к чату перед выполнением функции"""
    @wraps(func)
    async def wrapper(tg_chat_id: int, *args, **kwargs):
        try:
            await bot.get_chat(tg_chat_id)
            return await func(tg_chat_id, *args, **kwargs)
        except Exception as e:
            logging.error(CHAT_ACCESS_ERROR.format(tg_chat_id, e))
            await send_log_notification(LogNotification.ERROR, CHAT_ACCESS_ERROR.format(tg_chat_id, e))
            return False
    return wrapper