from aiogram.fsm.context import FSMContext
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import logging

from app.bot.schedule.schedule_utils import get_scheduler
from app.bot.service.auto_cancel_spot_service import auto_cancel_spot

async def schedule_spot_cancellation(state: FSMContext, confirmation_data, delay_minutes: int = 15):
    """
    Планирует автоматическую отмену места через указанное время
    """
    scheduler = get_scheduler()

    # Время срабатывания = текущее время + задержка
    run_time = datetime.now() + timedelta(minutes=delay_minutes)

    job_id = f"auto_cancel_{confirmation_data.tg_user_id}_{confirmation_data.assignment_date}"

    scheduler.add_job(
        auto_cancel_spot,
        trigger=DateTrigger(run_date=run_time),
        args=[state, confirmation_data],
        id=job_id,
        replace_existing=True
    )

    logging.info(f"Scheduled auto-cancel job {job_id} for {run_time}")
    return run_time