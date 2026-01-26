from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.handlers import setup_handlers


def setup_dispatcher() -> Dispatcher:
    """Настройка и конфигурация диспетчера"""
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Настройка обработчиков
    setup_handlers(dp)

    return dp