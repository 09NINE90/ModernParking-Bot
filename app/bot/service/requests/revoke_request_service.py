import logging
from datetime import date

import psycopg2
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.constants.log_types import LogNotification
from app.bot.keyboard_markup import return_markup, revoke_requests_markup, confirmation_revoke_requests_markup, \
    back_to_revoke_request_markup
from app.bot.notification.log_notification import send_log_notification
from app.bot.service.distribution_service import distribute_parking_spots
from app.bot.service.release.release_service import revoke_parking_release
from app.bot.service.requests.request_service import get_user_requests_for_revoke, get_request_for_confirm_revoke, \
    update_request_status
from app.bot.service.user_service import get_db_user_id, minus_one_user_rating
from app.data.init_db import get_db_connection
from app.data.models.releases.releases_enum import ParkingReleaseStatus
from app.data.models.requests.requests_enum import ParkingRequestStatus
from app.data.models.requests.revoke_requests import RevokeRequest
from app.log_text import DB_USER_ID_GET_ERROR, DATABASE_ERROR, UNEXPECTED_ERROR, USER_MINUS_RATING_ERROR


async def show_revoke_request_keyboard(query: CallbackQuery, state: FSMContext):
    today = date.today()
    tg_user_id = query.from_user.id

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                db_user_id = await get_db_user_id(cur, tg_user_id)

                if not db_user_id:
                    logging.error(DB_USER_ID_GET_ERROR.format(tg_user_id))
                    await send_log_notification(LogNotification.ERROR, DB_USER_ID_GET_ERROR.format(tg_user_id))
                    return None

                requests = await get_user_requests_for_revoke(cur, db_user_id)
                if not requests:
                    await query.message.edit_text(
                        text="Не найдено актуальных дат для отмены бронирования места",
                        reply_markup=return_markup
                    )
                    return None

                message_text = f"Список дат, на которые вы запрашивали места от <u>{today.strftime('%d.%m.%Y')}</u>:"
                markup = revoke_requests_markup(requests)
                await query.message.edit_text(
                    text=message_text,
                    reply_markup=markup
                )

    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))

    except Exception as e:
        logging.error(UNEXPECTED_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, UNEXPECTED_ERROR.format(e))


async def confirmation_revoke_request(query: CallbackQuery, state: FSMContext, request_id):
    tg_user_id = query.from_user.id

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                db_user_id = await get_db_user_id(cur, tg_user_id)

                if not db_user_id:
                    logging.error(DB_USER_ID_GET_ERROR.format(tg_user_id))
                    await send_log_notification(LogNotification.ERROR, DB_USER_ID_GET_ERROR.format(tg_user_id))
                    return None

                request: RevokeRequest = await get_request_for_confirm_revoke(cur, request_id, db_user_id)
                if not request.spot_id:
                    markup_text = 'отозвать'
                    message_text = (f"Вы уверены, что хотите <b>отозвать запрос</b> "
                                    f"на парковочное место на дату <u>{request.request_date.strftime('%d.%m.%Y')}</u>?\n\n"
                                    f"⚠️ <i>После этого вы больше не будете участвовать в распределении "
                                    f"парковочных мест на эту дату</i>")
                else:
                    markup_text = 'отказаться'
                    message_text = (f"Вы уверены, что хотите <b>отказаться от места "
                                    f"№{request.spot_id}</b> на дату <u>{request.request_date.strftime('%d.%m.%Y')}</u>?\n\n"
                                    f"⚠️ <i>После этого вы больше не будете участвовать в распределении "
                                    f"парковочных мест на эту дату</i>")

                await query.message.edit_text(
                    text=message_text,
                    reply_markup=confirmation_revoke_requests_markup(request, markup_text)
                )

    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))

    except Exception as e:
        logging.error(UNEXPECTED_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, UNEXPECTED_ERROR.format(e))


async def confirm_revoke_request(query: CallbackQuery, state: FSMContext, request_id):
    tg_user_id = query.from_user.id

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                db_user_id = await get_db_user_id(cur, tg_user_id)

                if not db_user_id:
                    logging.error(DB_USER_ID_GET_ERROR.format(tg_user_id))
                    await send_log_notification(LogNotification.ERROR, DB_USER_ID_GET_ERROR.format(tg_user_id))
                    return None

                request: RevokeRequest = await get_request_for_confirm_revoke(cur, request_id, db_user_id)
                if not request.spot_id:
                    await update_request_status(cur, request_id, ParkingRequestStatus.CANCELED)

                    message_text = (f"Вы успешно отозвали запрос на парковочное место "
                                    f"на дату <u>{request.request_date.strftime('%d.%m.%Y')}</u>")
                else:
                    await revoke_parking_release(cur, request.release_id, ParkingReleaseStatus.PENDING)
                    await update_request_status(cur, request_id, ParkingRequestStatus.CANCELED)
                    is_rating_change = await minus_one_user_rating(cur, db_user_id)
                    if not is_rating_change:
                        logging.error(USER_MINUS_RATING_ERROR.format(db_user_id, tg_user_id))
                        await send_log_notification(LogNotification.ERROR,
                                                    USER_MINUS_RATING_ERROR.format(db_user_id, tg_user_id))

                    message_text = (f"Вы успешно отказались от парковочного места <b>№{request.spot_id}</b> "
                                    f"на дату <u>{request.request_date.strftime('%d.%m.%Y')}</u>\n\n"
                                    f"ℹ️ <i>Это место будет предложено кому-нибудь другому</i>")


                await distribute_parking_spots()


                await query.message.edit_text(
                    text=message_text,
                    reply_markup=back_to_revoke_request_markup
                )

    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))

    except Exception as e:
        logging.error(UNEXPECTED_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, UNEXPECTED_ERROR.format(e))
