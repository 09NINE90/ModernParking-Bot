from app.bot.notification.delete_message import delete_message
from app.bot.notification.messages import to_user_about_time_confirmation_spent_by_reminder
from app.bot.notification.notify_user import notify_user
from app.bot.utils import get_user_full_mention
from app.data import get_db_connection
from app.data.models import ParkingReminder, ParkingReleaseStatus, ParkingRequestStatus
from app.logs.log_builder import log, LogType
from app.services import ServiceFactory


async def auto_cancel_reminder(reminder_data: ParkingReminder):
    """
        Автоматически отменяет место если пользователь не подтвердил вовремя
    """
    try:
        request_id = reminder_data.request_id
        release_id = reminder_data.release_id
        db_user_id = reminder_data.db_user_id
        tg_user_id = reminder_data.user_tg_id

        with get_db_connection() as conn:
            user_service = ServiceFactory.create_user_service(conn)
            reminder_service = ServiceFactory.create_reminder_spot_service(conn)
            spot_release_service = ServiceFactory.create_spot_release_service(conn)
            spot_request_service = ServiceFactory.create_spot_request_service(conn)

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
            sent_message_id = reminder_service.get_message_sent_id(
                user_id=db_user_id,
                request_id=request_id,
                release_id=release_id,
            )
            user_service.update_user_rating_by_user_id(
                db_user_id=db_user_id,
                delta=-1
            )

            conn.commit()

            message_text = await to_user_about_time_confirmation_spent_by_reminder(reminder_data)
            await notify_user(
                tg_user_id=tg_user_id,
                message_text=message_text
            )

            await delete_message(
                chat_id=tg_user_id,
                message_id=sent_message_id
            )

            request_status = spot_request_service.get_request_status_by_id(request_id)
            release_status = spot_release_service.get_release_status_by_id(release_id)
            user_name = await get_user_full_mention(tg_user_id, False)
            await log(
                log_type=LogType.INFO,
                log_message=f"{user_name} не успел подтвердить занятое место\n"
                            f"Запрос отменен автоматически"
                            f"release_status = {release_status}\n"
                            f"request_status = {request_status}"
            )

            from app.bot.handlers.callbacks.utils.distribution_spots_util import distribute_parking_spots
            await distribute_parking_spots()

    except Exception as e:
        await log(
            log_message=f"Ошибка автоматической отмены места после напоминания: {e}"
        )
