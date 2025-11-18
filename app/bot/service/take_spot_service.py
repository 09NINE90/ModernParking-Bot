import logging
from aiogram.types import CallbackQuery

from app.bot.constants.log_types import LogNotification
from app.bot.dto.spot_confirmation_dto import SpotConfirmationDTO
from app.bot.keyboard_markup import return_markup
from app.bot.notification.log_notification import send_log_notification
from app.data.init_db import get_db_connection
from app.data.repository.spot_confirmations_repository import find_spot_confirmations_by_user, \
    deactivate_spot_confirmations_by_user
from app.data.repository.users_repository import get_user_id_by_tg_id
from app.log_text import SPOT_TAKING_ERROR
from app.schedule.schedule_utils import cancel_scheduled_cancellation
from app.bot.service.distribution_service import distribute_parking_spots
from app.bot.service.process_confirmation_spot_service import process_spot_confirmation


async def take_spot(query: CallbackQuery):
    """Подтверждает занятие парковочного места пользователем."""
    user_tg_id = query.from_user.id

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                db_user_id = await get_user_id_by_tg_id(cur, user_tg_id)
                result = await find_spot_confirmations_by_user(cur, db_user_id)
                spot_confirmations = SpotConfirmationDTO(db_user_id=result[0],
                                                         tg_user_id=result[1],
                                                         spot_number=result[2],
                                                         assignment_date=result[3],
                                                         release_id=result[4],
                                                         request_id=result[5])

                if not spot_confirmations:
                    logging.warning(f"❌ No confirmation data found for user {user_tg_id}")
                    await query.message.edit_text("❌ Данные о месте устарели.")
                    return

                logging.debug(
                    f"Attempting to cancel scheduled auto-cancellation for "
                    f"spot #{spot_confirmations.spot_number}, user {user_tg_id}"
                )
                await cancel_scheduled_cancellation(spot_confirmations)

                logging.debug(
                    f"Processing confirmation for user {user_tg_id}, spot #{spot_confirmations.spot_number}"
                )
                success = await process_spot_confirmation(spot_confirmations)

                if success:
                    await query.message.edit_text(
                        f"✅ Вы успешно заняли место #{spot_confirmations.spot_number} "
                        f"на {spot_confirmations.assignment_date.strftime('%d.%m.%Y')}",
                        reply_markup=return_markup
                    )
                else:
                    logging.warning(f"Spot #{spot_confirmations.spot_number} already taken (user {user_tg_id})")
                    await send_log_notification(LogNotification.WARN,
                                                f"Spot #{spot_confirmations.spot_number} already taken (user {user_tg_id})")
                    await query.message.edit_text(
                        "❌ Не удалось занять место. Возможно, оно уже занято.",
                        reply_markup=return_markup
                    )

                await deactivate_spot_confirmations_by_user(cur, db_user_id)
    except Exception as e:
        logging.error(SPOT_TAKING_ERROR.format(user_tg_id, e))
        await send_log_notification(LogNotification.ERROR, SPOT_TAKING_ERROR.format(user_tg_id, e))
        await query.message.edit_text(
            "❌ Произошла ошибка при занятии места.",
            reply_markup=return_markup
        )

    finally:
        logging.debug(f"Triggering distribution after user {user_tg_id} action")
        await distribute_parking_spots()
