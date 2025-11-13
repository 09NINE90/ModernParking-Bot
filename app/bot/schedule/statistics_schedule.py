from datetime import datetime, timedelta

from apscheduler.triggers.cron import CronTrigger

from app.bot.service.statistics_service import statistics_service
from apscheduler.schedulers.asyncio import AsyncIOScheduler

def setup_scheduler():
    scheduler = AsyncIOScheduler()

    # Ежедневно в 7:30 ТОЛЬКО по будням (понедельник-пятница)
    scheduler.add_job(
        statistics_service,
        trigger=CronTrigger(
            hour=7,
            minute=30,
            day_of_week='mon-fri'
        ),
        args=[datetime.today()],
        id='daily_morning_statistics'
    )

    # Ежедневно в 18:30 ТОЛЬКО по будням (понедельник-пятница)
    scheduler.add_job(
        statistics_service,
        trigger=CronTrigger(
            hour=18,
            minute=30,
            day_of_week='mon-fri'
        ),
        args=[datetime.today() + timedelta(days=1)],
        id='daily_evening_statistics'
    )

    return scheduler