import asyncio
import logging
import sys
import signal

from app.bot.bot import bot
from app.bot.dispatcher import setup_dispatcher
from app.data.database import init_database
from app.config.settings import settings
from app.scheduler.schedule_utils import init_scheduler
from app.scheduler.scheduler import setup_scheduler


async def main():
    # Настройка логирования
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting bot application...")

    scheduler = None

    try:
        # Инициализация базы данных
        logger.info("Initializing database...")
        init_database()

        # Настройка планировщика
        logger.info("Setting up scheduler...")
        scheduler = setup_scheduler()
        init_scheduler(scheduler)
        scheduler.start()

        # Настройка и запуск бота
        logger.info("Setting up bot dispatcher...")
        dp = setup_dispatcher()

        logger.info("Starting bot polling...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

    finally:
        if scheduler and scheduler.running:
            scheduler.shutdown()
            logger.info("Scheduler stopped")

        logger.info("Bot application stopped")


def signal_handler(signum, frame):
    """Обработчик сигналов для graceful shutdown"""
    logging.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        logging.error(f"Application error: {e}")
        sys.exit(1)
