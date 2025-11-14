from aiogram import Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from app.bot.handlers import register_handlers

dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)
register_handlers(router)