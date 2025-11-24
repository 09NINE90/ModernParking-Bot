from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import logging

from app.bot.service.reminder_spot.auto_cancel_reminder import auto_cancel_reminder
from app.data.models.spot_reminder.parking_reminder_dto import ParkingReminder
from app.schedule.schedule_utils import get_scheduler
from app.bot.service.spots.auto_cancel_spot_service import auto_cancel_spot


async def schedule_spot_cancellation(confirmation_data, delay_minutes: int = 15):
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

    logging.debug(f"Scheduled auto-cancel job {job_id} for {run_time}")
    return run_time


async def schedule_reminder_cancellation(reminder_data: ParkingReminder, delay_hours=5.83):
    """
        Планирует автоматическую отмену занятия места пользователем
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

    logging.debug(f"Scheduled auto-cancel-reminder job {job_id} for {run_time}")
    return run_time
