import logging
import asyncio

from app.bot import dp
from app.bot.config import bot
from app.schedule.schedule_utils import init_scheduler
from app.schedule.statistics_schedule import setup_scheduler
from app.data.init_db import init_database

async def main():
    # Инициализация базы данных
    init_database()

    logging.basicConfig(
        level=logging.WARN,
        format='%(asctime)s - %(filename)s - %(funcName)s - %(lineno)d - %(name)s - %(levelname)s - %(message)s'
    )

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
