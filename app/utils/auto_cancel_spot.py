from datetime import datetime

from app.bot.notification.delete_message import delete_message
from app.bot.notification.enumz import NotificationTypes
from app.bot.notification.messages import to_user_about_time_confirmation_spent
from app.bot.notification.notify_user import notify_user
from app.bot.utils import get_user_full_mention
from app.data import get_db_connection
from app.data.models import ParkingReleaseStatus, ParkingRequestStatus, SpotConfirmationDTO, ConfirmationStatus
from app.logs.log_builder import log, LogType
from app.services import ServiceFactory
from app.utils.daily_statistics_util import update_daily_statistics_by_date


async def auto_cancel_spot(confirmation_data: SpotConfirmationDTO):
    try:
        request_id = confirmation_data.request_id
        release_id = confirmation_data.release_id
        db_user_id = confirmation_data.db_user_id
        tg_user_id = confirmation_data.tg_user_id
        confirmation_id = confirmation_data.confirmation_id

        with get_db_connection() as conn:
            spot_release_service = ServiceFactory.create_spot_release_service(conn)
            spot_request_service = ServiceFactory.create_spot_request_service(conn)
            spot_confirmation_service = ServiceFactory.create_spot_confirmation_service(conn)

            spot_release_service.update_parking_release_set_free(release_id, ParkingReleaseStatus.PENDING)
            spot_request_service.update_parking_request_status(request_id, ParkingRequestStatus.PENDING)
            spot_confirmation_service.set_status(confirmation_id, ConfirmationStatus.CANCELLED)

            message_sent_id = spot_confirmation_service.get_message_sent_id(confirmation_id)

            message_text = await to_user_about_time_confirmation_spent(confirmation_data)
            await notify_user(confirmation_data.tg_user_id, message_text, NotificationTypes.WITHOUT_MARKUP)

            await delete_message(
                chat_id=tg_user_id,
                message_id=message_sent_id
            )

            request_status = spot_request_service.get_request_status_by_id(confirmation_data.request_id)
            release_status = spot_release_service.get_release_status_by_id(confirmation_data.release_id)
            user_name = await get_user_full_mention(tg_user_id, False)
            await log(
                log_type=LogType.INFO,
                log_message=f"{user_name} не успел принять место\n"
                            f"Запрос отменен автоматически\n"
                            f"release_status = {release_status}\n"
                            f"request_status = {request_status}"
            )
            conn.commit()

            datetime_now = datetime.now()
            await update_daily_statistics_by_date(datetime_now)

            from app.bot.handlers.callbacks.utils.distribution_spots_util import distribute_parking_spots
            await distribute_parking_spots()


    except Exception as e:
        await log(
            log_message=f"Ошибка автоматической отмены предложенного места: {e}"
        )
