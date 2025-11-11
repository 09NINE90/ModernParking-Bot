import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
import asyncio

from bot_keyboards import main_markup
from app.callbacks.back_to_main_menu import back_to_main_menu
from app.callbacks.register_user import register_user
from app.callbacks.release_spot import select_spot, process_spot_release, handle_spot_number
from db_config import init_database
from parking_states import ParkingStates

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')

def register_handlers():
    router.message.register(start, Command("start"))
    router.message.register(handle_spot_number, ParkingStates.waiting_for_spot_number)
    router.callback_query.register(handle_callback)

async def start(message: types.Message):
    user = message.from_user
    await register_user(user)

    await message.answer(
        "🚗 Бот распределения парковочных мест\n\n"
        "Выберите действие:",
        reply_markup=main_markup
    )

async def handle_callback(query: CallbackQuery, state: FSMContext):
    data = query.data

    match data:
        case "release_spot":
            await select_spot(query, state)
        case str() if data.startswith("release_date_"):
            date_str = data.replace("release_date_", "")
            await process_spot_release(query, date_str, state)
        # case "request_spot":
        #     await self.show_request_calendar(query)
        # case str() if data.startswith("request_date_"):
        #     date_str = data.replace("request_date_", "")
        #     await self.process_spot_request(query, date_str)
        # case "my_stats":
        #     await self.show_user_stats(query)
        # case "available_spots":
        #     await self.show_available_spots(query)
        case "back_to_main":
            await back_to_main_menu(query)

async def run():
    """Запуск бота"""
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    router = Router()
    dp.include_router(router)
    init_database()
    register_handlers()

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("Бот остановлен")
