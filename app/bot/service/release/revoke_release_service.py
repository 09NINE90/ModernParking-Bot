import logging
from datetime import date

import psycopg2
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.constants.log_types import LogNotification
from app.bot.keyboard_markup import return_markup, revoke_releases_markup, confirmation_revoke_release_markup, \
    back_to_revoke_release_markup
from app.bot.notification.log_notification import send_log_notification
from app.bot.service.distribution_service import distribute_parking_spots
from app.bot.service.release.release_service import get_user_releases_for_revoke, get_release_for_confirm_revoke, \
    revoke_parking_release
from app.bot.service.user_service import get_db_user_id
from app.data.init_db import get_db_connection
from app.data.models.releases.releases_enum import ParkingReleaseStatus
from app.data.models.releases.revoke_releases import RevokeRelease
from app.log_text import DB_USER_ID_GET_ERROR, DATABASE_ERROR, UNEXPECTED_ERROR


async def show_revoke_release_keyboard(query: CallbackQuery, state: FSMContext):
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

                releases = await get_user_releases_for_revoke(cur, db_user_id)
                if not releases:
                    await query.message.edit_text(
                        text="У вас нет освобожденных мест, которые никто не занял",
                        reply_markup=return_markup
                    )
                    return None

                message_text = f"Список мест, которые вы освободили от <u>{today.strftime('%d.%m.%Y')}</u>:"
                markup = revoke_releases_markup(releases)
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


async def confirmation_revoke_release(query: CallbackQuery, state: FSMContext, release_id):
    tg_user_id = query.from_user.id

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                db_user_id = await get_db_user_id(cur, tg_user_id)

                if not db_user_id:
                    logging.error(DB_USER_ID_GET_ERROR.format(tg_user_id))
                    await send_log_notification(LogNotification.ERROR, DB_USER_ID_GET_ERROR.format(tg_user_id))
                    return None

                release: RevokeRelease = await get_release_for_confirm_revoke(cur, release_id, db_user_id)
                if release.status == ParkingReleaseStatus.ACCEPTED or release.status == ParkingReleaseStatus.WAITING:
                    await query.message.edit_text(
                        text="⚠️ Место уже кому-то предложили",
                        reply_markup=back_to_revoke_release_markup
                    )
                    return None

                message_text = (f"Вы уверены, что хотите <b>отозвать место №{release.spot_id}</b> "
                                f"на дату <u>{release.release_date.strftime('%d.%m.%Y')}</u>?\n\n"
                                f"⚠️ <i>Если место никто не занял, то оно успешно отзовется</i>")

                await query.message.edit_text(
                    text=message_text,
                    reply_markup=confirmation_revoke_release_markup(release)
                )

    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))

    except Exception as e:
        logging.error(UNEXPECTED_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, UNEXPECTED_ERROR.format(e))


async def confirm_revoke_release(query: CallbackQuery, state: FSMContext, release_id):
    tg_user_id = query.from_user.id

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                db_user_id = await get_db_user_id(cur, tg_user_id)

                if not db_user_id:
                    logging.error(DB_USER_ID_GET_ERROR.format(tg_user_id))
                    await send_log_notification(LogNotification.ERROR, DB_USER_ID_GET_ERROR.format(tg_user_id))
                    return None

                release: RevokeRelease = await get_release_for_confirm_revoke(cur, release_id, db_user_id)
                if release.status == ParkingReleaseStatus.ACCEPTED or release.status == ParkingReleaseStatus.WAITING:
                    await query.message.edit_text(
                        text="⚠️ Место уже кому-то предложили",
                        reply_markup=back_to_revoke_release_markup
                    )
                    return None

                await revoke_parking_release(cur, release.release_id, ParkingReleaseStatus.CANCELED)

                await distribute_parking_spots()

                message_text = (f"Вы успешно отозвали место <b>№{release.spot_id} </b>"
                                f"на дату <u>{release.release_date.strftime('%d.%m.%Y')}</u>\n\n"
                                f"ℹ️ <i>Это больше не будет назначаться никому в эту дату</i>")

                await query.message.edit_text(
                    text=message_text,
                    reply_markup=back_to_revoke_release_markup
                )

    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))

    except Exception as e:
        logging.error(UNEXPECTED_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, UNEXPECTED_ERROR.format(e))
