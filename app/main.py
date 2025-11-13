import logging
import asyncio

from aiogram import Dispatcher, Router
from aiogram.filters import Command

from app.bot import bot
from app.bot.callbacks.handle_callback import handle_callback
from app.bot.commands.start import start
from app.bot.commands.statistics import statistics
from app.bot.schedule.schedule_utils import init_scheduler
from app.bot.schedule.statistics_schedule import setup_scheduler
from app.data.init_db import init_database
from app.bot.callbacks.release_spot import handle_spot_number
from app.bot.parking_states import ParkingStates

def register_handlers(router):
    router.message.register(start, Command("start"))
    router.message.register(statistics, Command("statistics"))
    router.message.register(handle_spot_number, ParkingStates.waiting_for_spot_number)
    router.callback_query.register(handle_callback)

async def main():
    # Инициализация базы данных
    init_database()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Создание диспетчера и роутера
    dp = Dispatcher()
    router = Router()
    dp.include_router(router)
    register_handlers(router)

    # Запуск планировщика
    scheduler = setup_scheduler()
    init_scheduler(scheduler)
    scheduler.start()

    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
