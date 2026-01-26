from aiogram import Dispatcher, Router


def setup_callbacks(dp: Dispatcher) -> None:
    """
        Настройка всех callback обработчиков
    """
    # Создаем основной router для callback запросов
    callback_router = Router()

    from .base import setup_base_callbacks
    from .spots import setup_spots_callbacks
    from .found_spot import setup_found_spot_callbacks
    from .revoke import setup_revoke_callbacks
    from .my_statistics import setup_statistics_callbacks
    from .feedback import setup_feedback_callbacks
    from .default_schedule import setup_default_schedule_callbacks
    from .admin.admin_callbacks import setup_admin_callbacks
    from .reminder_spot import setup_reminder_spot_callbacks

    setup_base_callbacks(callback_router)
    setup_spots_callbacks(callback_router)
    setup_found_spot_callbacks(callback_router)
    setup_revoke_callbacks(callback_router)
    setup_statistics_callbacks(callback_router)
    setup_feedback_callbacks(callback_router)
    setup_default_schedule_callbacks(callback_router)
    setup_admin_callbacks(callback_router)
    setup_reminder_spot_callbacks(callback_router)

    dp.include_router(callback_router)


__all__ = [
    'setup_callbacks'
]
