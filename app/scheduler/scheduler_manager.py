from datetime import datetime, timedelta

from apscheduler.triggers.date import DateTrigger

from app.data.models import SpotConfirmationDTO, ParkingReminder
from app.logs.log_builder import log, LogType
from app.scheduler.schedule_utils import get_scheduler
from app.utils.auto_cancel_distribution import auto_cancel_distribution
from app.utils.auto_cancel_reminder_util import auto_cancel_reminder
from app.utils.auto_cancel_spot_util import auto_cancel_spot


async def schedule_spot_cancellation(confirmation_data: SpotConfirmationDTO, delay_minutes: int = 15):
    """
        Планирует автоматическую отмену места через указанное время
    """
    scheduler = get_scheduler()

    run_time = datetime.now() + timedelta(minutes=delay_minutes)

    job_id = f"auto_cancel_{confirmation_data.tg_user_id}_{confirmation_data.assignment_date}"

    scheduler.add_job(
        auto_cancel_spot,
        trigger=DateTrigger(run_date=run_time),
        args=[confirmation_data],
        id=job_id,
        replace_existing=True
    )

    await log(
        log_type=LogType.DEBUG,
        log_message=f"Scheduled auto-cancel job {job_id} for {run_time}",
        is_sending_log=False
    )
    return run_time


async def schedule_reminder_cancellation(reminder_data: ParkingReminder, delay_hours=6):
    """
        Планирует автоматическую отмену места через указанное время
        при напоминании пользователю о назначенном месте
    """
    scheduler = get_scheduler()

    run_time = datetime.now() + timedelta(hours=delay_hours)

    job_id = f"auto_cancel_reminder_{reminder_data.release_id}_{reminder_data.request_id}"

    scheduler.add_job(
        auto_cancel_reminder,
        trigger=DateTrigger(run_date=run_time),
        args=[reminder_data],
        id=job_id,
        replace_existing=True
    )

    await log(
        log_type=LogType.DEBUG,
        log_message=f"Scheduled auto-cancel-reminder job {job_id} for {run_time}",
        is_sending_log=False
    )
    return run_time

async def schedule_distribute_weekly_parking_schedules(tg_id, message_id, delay_hours=12):
    scheduler = get_scheduler()

    run_time = datetime.now() + timedelta(hours=delay_hours)

    job_id = f"auto_cancel_distribute_weekly_parking_{tg_id}"

    scheduler.add_job(
        auto_cancel_distribution,
        trigger=DateTrigger(run_date=run_time),
        args=[tg_id, message_id],
        id=job_id,
        replace_existing=True
    )

    await log(
        log_type=LogType.DEBUG,
        log_message=f"Scheduled auto-cancel-distribute_weekly_parking job {job_id} for {run_time}",
        is_sending_log=False
    )
    return run_time
