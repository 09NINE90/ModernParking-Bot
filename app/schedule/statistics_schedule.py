from apscheduler.triggers.cron import CronTrigger

from app.bot.service.reminder_spot.spot_reminder_service import spot_reminder
from app.bot.service.statistics_service import daily_statistics_service, weekly_statistics_service
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.data.service.update_statuses_service import update_statuses_service


def setup_scheduler():
    scheduler = AsyncIOScheduler()

    # Ежедневно в 7:30 ТОЛЬКО по будням (понедельник-пятница)
    scheduler.add_job(
        daily_statistics_service,
        trigger=CronTrigger(
            hour=7,
            minute=30,
            day_of_week='mon-fri'
        ),
        id='daily_morning_statistics'
    )

    # Ежедневно в 18:30 ТОЛЬКО по будням (понедельник-четверг)
    scheduler.add_job(
        daily_statistics_service,
        trigger=CronTrigger(
            hour=18,
            minute=30,
            day_of_week='mon-thu'
        ),
        args=[1],
        id='daily_evening_statistics'
    )

    # Ежедневно в 18:00
    scheduler.add_job(
        spot_reminder,
        trigger=CronTrigger(
            hour=18,
            minute=00
        ),
        id='daily_user_reminder'
    )

    # Еженедельно в пятницу в 18:30
    scheduler.add_job(
        weekly_statistics_service,
        trigger=CronTrigger(
            hour=18,
            minute=30,
            day_of_week='fri'
        ),
        id='weekly_statistics'
    )

    # Ежедневно в 00:05
    scheduler.add_job(
        update_statuses_service,
        trigger=CronTrigger(
            hour=0,
            minute=5,
        ),
        id='daily_updating_statuses'
    )

    return scheduler