import logging

import psycopg2
from aiogram.types import CallbackQuery

from app.bot.constants.log_types import LogNotification
from app.bot.notification.messages.to_owner_message import to_owner_message
from app.bot.notification.notify_user import notify_user
from app.bot.service.requests.request_service import update_request_status
from app.bot.users.get_user_full_mention import get_user_full_mention
from app.data.models.releases.releases_enum import ParkingReleaseStatus
from app.data.models.requests.requests_enum import ParkingRequestStatus
from app.data.models.spot_confirmation.spot_confirmation_dto import SpotConfirmationDTO
from app.bot.keyboard_markup import return_markup
from app.bot.notification.log_notification import send_log_notification
from app.bot.service.user_service import get_db_user_id
from app.data.init_db import get_db_connection
from app.data.repository.parking_releases_repository import update_parking_releases, get_release_owner, \
    get_release_status_by_id
from app.data.repository.parking_requests_repository import get_request_status_by_id
from app.data.repository.spot_confirmations_repository import find_spot_confirmations_by_user, \
    deactivate_spot_confirmations_by_user
from app.data.repository.users_repository import increment_user_rating
from app.log_text import SPOT_TAKING_ERROR, DB_USER_ID_GET_ERROR, DATABASE_ERROR
from app.schedule.schedule_utils import cancel_scheduled_cancellation


async def take_spot(query: CallbackQuery):
    """Подтверждает занятие парковочного места пользователем."""
    tg_user_id = query.from_user.id

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                db_user_id = await get_db_user_id(cur, tg_user_id)

                if not db_user_id:
                    logging.error(DB_USER_ID_GET_ERROR.format(tg_user_id))
                    await send_log_notification(LogNotification.ERROR, DB_USER_ID_GET_ERROR.format(tg_user_id))
                    return None
                
                result = await find_spot_confirmations_by_user(cur, db_user_id)
                if not result:
                    logging.warning(f"❌ No confirmation data found for user {tg_user_id}")
                    await query.message.edit_text("❌ Данные о месте устарели.")
                    return

                spot_confirmations = SpotConfirmationDTO(db_user_id=result[0],
                                                         tg_user_id=result[1],
                                                         spot_number=result[2],
                                                         assignment_date=result[3],
                                                         release_id=result[4],
                                                         request_id=result[5])

                await update_parking_releases(cur, db_user_id, spot_confirmations.release_id,
                                              ParkingReleaseStatus.ACCEPTED)
                await update_request_status(cur, spot_confirmations.request_id, ParkingRequestStatus.ACCEPTED)

                await cancel_scheduled_cancellation(spot_confirmations)

                release_owner = await get_release_owner(cur, spot_confirmations.release_id)
                if release_owner:
                    release_user_id, release_tg_id = release_owner
                    message_text = await to_owner_message(release_tg_id, spot_confirmations.spot_number,
                                                          spot_confirmations.assignment_date)
                    await notify_user(release_tg_id, message_text)

                await deactivate_spot_confirmations_by_user(cur, db_user_id)

                await increment_user_rating(cur, db_user_id)

                request_status = await get_request_status_by_id(cur, spot_confirmations.request_id)
                release_status = await get_release_status_by_id(cur, spot_confirmations.release_id)
                conn.commit()

                await query.message.edit_text(
                    f"✅ Вы успешно заняли место №{spot_confirmations.spot_number} "
                    f"на {spot_confirmations.assignment_date.strftime('%d.%m.%Y')}",
                    reply_markup=return_markup
                )
                logging.info(f"User {tg_user_id} successfully took spot #{spot_confirmations.spot_number}")
                user_name = await get_user_full_mention(tg_user_id, True)
                await send_log_notification(LogNotification.INFO,
                                            f"Пользователь {user_name} успешно занял место №{spot_confirmations.spot_number}\n"
                                            f"release_status = {release_status}\n"
                                            f"request_status = {request_status}")


    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))
    except Exception as e:
        logging.error(SPOT_TAKING_ERROR.format(tg_user_id, e))
        await send_log_notification(LogNotification.ERROR, SPOT_TAKING_ERROR.format(tg_user_id, e))
        await query.message.edit_text(
            "❌ Произошла ошибка при занятии места.",
            reply_markup=return_markup
        )

