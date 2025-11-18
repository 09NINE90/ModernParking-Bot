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
from app.log_text import SPOT_CANCEL_ERROR
from app.schedule.schedule_utils import cancel_scheduled_cancellation
from app.bot.service.distribution_service import distribute_parking_spots
from app.bot.service.process_confirmation_spot_service import process_spot_cancel

async def cancel_spot(query: CallbackQuery):
    """Обрабатывает отмену занятия места"""
    user_tg_id = query.from_user.id

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                db_user_id = await get_user_id_by_tg_id(cur, user_tg_id)
                result = await find_spot_confirmations_by_user(cur, db_user_id)
                print(result)
                spot_confirmations = SpotConfirmationDTO(db_user_id=result[0],
                                                         tg_user_id=result[1],
                                                         spot_number=result[2],
                                                         assignment_date=result[3],
                                                         release_id=result[4],
                                                         request_id=result[5])
                if not spot_confirmations:
                    await query.message.edit_text("❌ Данные о месте устарели")
                    return

                await cancel_scheduled_cancellation(spot_confirmations)

                success = await process_spot_cancel(spot_confirmations)

                if success:
                    await query.message.edit_text(
                        f"ℹ️ Вы успешно отказались от места #{spot_confirmations.spot_number} "
                        f"на {spot_confirmations.assignment_date.strftime('%d.%m.%Y')}\n"
                        "️️⚠️ Я больше не буду предлагать вам места на эту дату",
                        reply_markup=return_markup
                    )
                else:
                    await query.message.edit_text(
                        "❌ Не удалось занять место. Возможно, оно уже занято.",
                        reply_markup=return_markup
                    )

                await deactivate_spot_confirmations_by_user(cur, db_user_id)
    except Exception as e:
        logging.error(SPOT_CANCEL_ERROR.format(query.from_user.id, e))
        await send_log_notification(LogNotification.ERROR, SPOT_CANCEL_ERROR.format(query.from_user.id, e))
        await query.message.edit_text(
            "❌ Произошла ошибка при отклонении места",
            reply_markup=return_markup
        )
    finally:
        await distribute_parking_spots()