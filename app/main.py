import logging
import asyncio

from aiogram import Dispatcher, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot import bot
from app.bot.callbacks.request_spot import show_request_calendar, process_spot_request
from app.bot.commands.start import start
from app.bot.commands.statistics import statistics
from app.bot.schedule.statistics_schedule import setup_scheduler
from app.data.init_db import init_database
from app.bot.callbacks.back_to_main_menu import back_to_main_menu
from app.bot.callbacks.release_spot import select_spot, process_spot_release, handle_spot_number
from app.bot.parking_states import ParkingStates

def register_handlers(router):
    router.message.register(start, Command("start"))
    router.message.register(statistics, Command("statistics"))
    router.message.register(handle_spot_number, ParkingStates.waiting_for_spot_number)
    router.callback_query.register(handle_callback)

async def handle_callback(query: CallbackQuery, state: FSMContext):
    data = query.data

    match data:
        case "release_spot":
            await select_spot(query, state)
        case str() if data.startswith("release_date_"):
            date_str = data.replace("release_date_", "")
            await process_spot_release(query, date_str, state)
        case "request_spot":
            await show_request_calendar(query, state)
        case str() if data.startswith("request_date_"):
            date_str = data.replace("request_date_", "")
            await process_spot_request(query, date_str)
        # case "my_stats":
        #     await self.show_user_stats(query)
        # case "available_spots":
        #     await self.show_available_spots(query)
        case "back_to_main":
            await back_to_main_menu(query)

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
    scheduler.start()

    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
