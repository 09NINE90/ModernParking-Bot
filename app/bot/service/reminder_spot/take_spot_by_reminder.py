import logging

import psycopg2
from aiogram.types import CallbackQuery

from app.bot.constants.log_types import LogNotification
from app.bot.keyboard_markup import return_markup
from app.bot.notification.log_notification import send_log_notification
from app.bot.service.distribution_service import distribute_parking_spots
from app.bot.service.user_service import get_db_user_id
from app.data.init_db import get_db_connection
from app.data.models.spot_reminder.parking_reminder_dto import ParkingReminder
from app.data.repository.reminder_spot_confirmations_repository import find_reminder_spot_confirmations_by_user, \
    deactivate_reminder_spot_confirmations_by_user
from app.log_text import DB_USER_ID_GET_ERROR, DATABASE_ERROR, SPOT_TAKING_ERROR
from app.schedule.schedule_utils import cancel_scheduled_cancellation_by_reminder


async def take_spot_by_reminder(query: CallbackQuery):
    """Подтверждает занятие парковочного места пользователем."""
    tg_user_id = query.from_user.id

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                db_user_id = await get_db_user_id(cur, tg_user_id)

                if not db_user_id:
                    logging.error(DB_USER_ID_GET_ERROR.format(tg_user_id))
                    await send_log_notification(LogNotification.ERROR, DB_USER_ID_GET_ERROR.format(tg_user_id))
                    await query.message.edit_text(
                        "❌ Не удалось найти данные пользователя.",
                        reply_markup=return_markup
                    )
                    return None

                result = await find_reminder_spot_confirmations_by_user(cur, db_user_id)

                if not result:
                    logging.warning(f"❌ No reminder data found for user {tg_user_id}")
                    await query.message.edit_text("❌ Активное напоминание не найдено.")
                    return

                reminder_data = ParkingReminder(
                    spot_id=result[2],
                    user_tg_id=result[1],
                    db_user_id=result[0],
                    release_id=result[4],
                    release_date=result[3],
                    request_id=result[5]
                )

                logging.debug(
                    f"Attempting to cancel scheduled auto-cancellation for "
                    f"spot №{reminder_data.spot_id}, user {tg_user_id}"
                )
                await cancel_scheduled_cancellation_by_reminder(reminder_data)

                logging.debug(
                    f"Processing confirmation for user {tg_user_id}, spot №{reminder_data.spot_id}"
                )

                try:
                    await deactivate_reminder_spot_confirmations_by_user(cur, db_user_id)
                    await query.message.edit_text(
                        f"✅ Вы успешно подтвердили занятие места №{reminder_data.spot_id} "
                        f"на {reminder_data.release_date.strftime('%d.%m.%Y')}",
                        reply_markup=return_markup
                    )
                except Exception as e:
                    logging.warning(f"Spot #{reminder_data.spot_id} already taken (user {tg_user_id})")
                    await send_log_notification(LogNotification.WARN,
                                                f"Spot #{reminder_data.spot_id} already taken (user {tg_user_id})")
                    await query.message.edit_text(
                        "❌ Место уже занято другим пользователем.",
                        reply_markup=return_markup
                    )

    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))
        await query.message.edit_text(
            "❌ Ошибка подключения к базе данных.",
            reply_markup=return_markup
        )
    except Exception as e:
        logging.error(SPOT_TAKING_ERROR.format(tg_user_id, e))
        await send_log_notification(LogNotification.ERROR, SPOT_TAKING_ERROR.format(tg_user_id, e))
        await query.message.edit_text(
            "❌ Произошла непредвиденная ошибка.",
            reply_markup=return_markup
        )

    finally:
        logging.debug(f"Triggering distribution after user {tg_user_id} action")
        await distribute_parking_spots()