from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.utils.check_confirmation_status_util import expire_waiting_confirmations
from app.utils.daily_statistics_util import get_daily_statistics
from app.utils.distribute_weekly_schedules_util import distribute_weekly_schedules
from app.utils.spot_reminder_util import spot_reminder
from app.utils.update_statuses_util import update_statuses
from app.utils.weekly_statistics_util import get_weekly_statistics


def setup_scheduler() -> AsyncIOScheduler:
    """Настройка и конфигурация планировщика"""
    scheduler = AsyncIOScheduler()

    # Ежедневно в 7:30 ТОЛЬКО по будням (понедельник-пятница)
    scheduler.add_job(
        get_daily_statistics,
        trigger=CronTrigger(
            hour=7,
            minute=30,
            day_of_week='mon-fri'
        ),
        id='daily_morning_statistics'
    )

    # Ежедневно в 18:30 ТОЛЬКО по будням (понедельник-четверг)
    scheduler.add_job(
        get_daily_statistics,
        trigger=CronTrigger(
            hour=18,
            minute=30,
            day_of_week='mon-thu'
        ),
        args=[1],
        id='daily_evening_statistics'
    )

    # Еженедельно в пятницу в 18:30
    scheduler.add_job(
        get_weekly_statistics,
        trigger=CronTrigger(
            hour=19, # todo поставить 18:00
            minute=30,
            day_of_week='fri'
        ),
        id='weekly_statistics'
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

    # Ежедневно в 18:00
    scheduler.add_job(
        expire_waiting_confirmations,
        trigger=CronTrigger(
            hour=18,
            minute=00
        ),
        id='daily_check_confirmation_status'
    )

    # Ежедневно в 00:05
    scheduler.add_job(
        update_statuses,
        trigger=CronTrigger(
            hour=0,
            minute=5,
        ),
        id='daily_updating_statuses'
    )

    # Еженедельно в воскресение в 12:00
    scheduler.add_job(
        distribute_weekly_schedules,
        trigger=CronTrigger(
            hour=12,
            minute=00,
            day_of_week='sun'
        ),
        id='distribute_weekly_parking_schedules'
    )

    return scheduler
