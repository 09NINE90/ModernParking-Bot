from functools import wraps

from app.bot import bot
from app.logs.log_builder import log_sync


def chat_access_required(func):
    """Декоратор для проверки доступа к чату перед выполнением функции"""
    @wraps(func)
    async def wrapper(tg_chat_id: int, *args, **kwargs):
        try:
            await bot.get_chat(tg_chat_id)
            return await func(tg_chat_id, *args, **kwargs)
        except Exception as e:
            log_sync(
                log_message=f"Ошибка получения доступа к чату {tg_chat_id}: {e}"
            )
            return False
    return wrapper