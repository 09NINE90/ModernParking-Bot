import logging

from aiogram.fsm.context import FSMContext

from app.bot.notification.notify_user_about_time_confirmation_spent import notify_user_about_time_confirmation_spent
from app.bot.service.spot_confirmation_service import process_spot_cancel


async def auto_cancel_spot(state: FSMContext ,confirmation_data):
    """
    Автоматически отменяет место если пользователь не подтвердил вовремя
    """
    try:
        logging.info(f"Auto-canceling spot for user {confirmation_data.tg_user_id}, "
                     f"spot #{confirmation_data.spot_number} on {confirmation_data.assignment_date}")

        success = await process_spot_cancel(confirmation_data)

        if success:
            # Импортируем здесь, чтобы избежать циклической зависимости
            await notify_user_about_time_confirmation_spent(confirmation_data)

            from app.bot.service.distribution_service import distribute_parking_spots
            await distribute_parking_spots(state)
        else:
            logging.error(f"Failed to auto-cancel spot for user {confirmation_data.tg_user_id}")

    except Exception as e:
        logging.error(f"Error in auto_cancel_spot: {e}")