from apscheduler.triggers.cron import CronTrigger

from app.bot.service.statistics_service import statistics_service
from apscheduler.schedulers.asyncio import AsyncIOScheduler

def setup_scheduler():
    scheduler = AsyncIOScheduler()

    # Ежедневно в 7:30
    scheduler.add_job(
        statistics_service,
        trigger=CronTrigger(hour=7, minute=30),
        id='daily_statistics'
    )

    return scheduler