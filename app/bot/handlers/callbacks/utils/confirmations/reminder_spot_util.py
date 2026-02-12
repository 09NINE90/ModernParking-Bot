from aiogram.types import CallbackQuery

from app.bot.keyboards import back_to_main_markup
from app.data import get_db_connection
from app.data.models import ParkingReleaseStatus, ParkingRequestStatus
from app.scheduler.schedule_utils import cancel_scheduled_cancellation_by_reminder
from app.services import ServiceFactory
from app.utils.emoji_util import info_emoji, warn_emoji, sber_emoji


async def take_spot_by_reminder(callback: CallbackQuery):
    """Подтверждает занятие парковочного места пользователем."""

    tg_user_id = callback.from_user.id

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)
        reminder_service = ServiceFactory.create_reminder_spot_service(conn)

        db_user_id = user_service.get_db_user_id_by_tg_id(tg_user_id)
        if not db_user_id:
            return None

        reminder_data = reminder_service.get_reminder_spot_confirmations_by_user(
            user_id=db_user_id,
        )

        await cancel_scheduled_cancellation_by_reminder(reminder_data)

        reminder_service.deactivate_reminder_spot_confirmations_by_user(
            user_id=db_user_id,
        )

        conn.commit()

        await callback.message.edit_text(
            f"{sber_emoji} Вы успешно подтвердили занятие места №{reminder_data.spot_id} "
            f"на {reminder_data.release_date.strftime('%d.%m.%Y')}",
            reply_markup=back_to_main_markup
        )

        return None


async def cancel_spot_by_reminder(callback: CallbackQuery):
    """Обрабатывает отмену занятия места"""

    tg_user_id = callback.from_user.id

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)
        reminder_service = ServiceFactory.create_reminder_spot_service(conn)
        spot_release_service = ServiceFactory.create_spot_release_service(conn)
        spot_request_service = ServiceFactory.create_spot_request_service(conn)

        db_user_id = user_service.get_db_user_id_by_tg_id(tg_user_id)
        if not db_user_id:
            return None

        reminder_data = reminder_service.get_reminder_spot_confirmations_by_user(
            user_id=db_user_id,
        )

        request_id = reminder_data.request_id
        release_id = reminder_data.release_id

        await cancel_scheduled_cancellation_by_reminder(reminder_data)

        spot_release_service.update_parking_releases(
            user_id=db_user_id,
            release_id=release_id,
            current_status=ParkingReleaseStatus.PENDING
        )
        spot_request_service.update_parking_request_status(
            request_id=request_id,
            current_status=ParkingRequestStatus.CANCELED
        )
        reminder_service.deactivate_reminder_spot_confirmations_by_user(
            user_id=db_user_id,
        )

        conn.commit()

        await callback.message.edit_text(
            f"{info_emoji} Вы успешно отказались от места №{reminder_data.spot_id} "
            f"на {reminder_data.release_date.strftime('%d.%m.%Y')}\n\n"
            f"️{warn_emoji} <i>Я больше не буду предлагать Вам места на эту дату</i>",
            reply_markup=back_to_main_markup
        )

        from app.bot.handlers.callbacks.utils.distribution_spots_util import distribute_parking_spots
        await distribute_parking_spots()

        return None
