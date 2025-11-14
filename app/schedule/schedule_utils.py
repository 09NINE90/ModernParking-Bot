from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

_scheduler = None


def init_scheduler(scheduler_instance: AsyncIOScheduler):
    """Инициализирует глобальный scheduler"""
    global _scheduler
    _scheduler = scheduler_instance


def get_scheduler() -> AsyncIOScheduler:
    """Возвращает глобальный scheduler"""
    if _scheduler is None:
        raise RuntimeError("Scheduler not initialized. Call init_scheduler first.")
    return _scheduler


def cancel_scheduled_cancellation(confirmation_data):
    """
    Отменяет запланированную автоматическую отмену места
    """
    try:
        scheduler = get_scheduler()
        job_id = f"auto_cancel_{confirmation_data.tg_user_id}_{confirmation_data.assignment_date}"

        job = scheduler.get_job(job_id)
        if job:
            scheduler.remove_job(job_id)
            logging.debug(f"Cancelled scheduled job: {job_id}")
            return True
        return False

    except Exception as e:
        logging.error(f"Error cancelling scheduled job: {e}")
        return False
