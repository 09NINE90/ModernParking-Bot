from datetime import date

from aiogram.types import CallbackQuery

from app.bot.keyboards import back_to_main_markup
from app.bot.keyboards.inline import revoke_releases_markup, back_to_revoke_release_markup, \
    confirmation_revoke_release_markup
from app.bot.utils import get_user_full_mention
from app.data import get_db_connection
from app.data.models import RevokeRelease, ParkingReleaseStatus
from app.logs.log_builder import log, LogType
from app.services import ServiceFactory


async def choose_release_for_revocation(callback: CallbackQuery):
    today = date.today()
    tg_user_id = callback.from_user.id

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)
        spot_release_service = ServiceFactory.create_spot_release_service(conn)

        db_user_id = user_service.get_db_user_id_by_tg_id(tg_user_id)
        if not db_user_id:
            return None

        releases_for_revoke = spot_release_service.get_user_releases_for_revoke(
            db_user_id=db_user_id,
            rq_date=today
        )
        if releases_for_revoke is None:
            await callback.message.edit_text(
                text="У вас нет освобожденных мест, которые никто не занял",
                reply_markup=back_to_main_markup
            )
            return None

        message_text = f"Список мест, которые вы освободили от <u>{today.strftime('%d.%m.%Y')}</u>:"
        markup = revoke_releases_markup(releases_for_revoke)
        await callback.message.edit_text(
            text=message_text,
            reply_markup=markup
        )

    return None


async def confirmation_revoke_release(callback: CallbackQuery, release_id):
    tg_user_id = callback.from_user.id

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)
        spot_release_service = ServiceFactory.create_spot_release_service(conn)

        db_user_id = user_service.get_db_user_id_by_tg_id(tg_user_id)
        if not db_user_id:
            return None

        release: RevokeRelease = spot_release_service.get_release_for_confirm_revoke(
            db_user_id=db_user_id,
            release_id=release_id
        )
        if release.status == ParkingReleaseStatus.ACCEPTED:
            await callback.message.edit_text(
                text="⚠️ Место уже кому-то отдано",
                reply_markup=back_to_revoke_release_markup
            )
            return None
        elif release.status == ParkingReleaseStatus.WAITING:
            await callback.message.edit_text(
                text="⚠️ Место уже кому-то предложили",
                reply_markup=back_to_revoke_release_markup
            )
            return None

        message_text = (f"Вы уверены, что хотите <b>отозвать место №{release.spot_id}</b> "
                        f"на дату <u>{release.release_date.strftime('%d.%m.%Y')}</u>?\n\n"
                        f"⚠️ <i>Если место никто не занял, то оно успешно отзовется</i>")

        await callback.message.edit_text(
            text=message_text,
            reply_markup=confirmation_revoke_release_markup(release)
        )

    return None


async def confirm_revoke_release(callback: CallbackQuery, release_id):
    tg_user_id = callback.from_user.id

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)
        spot_release_service = ServiceFactory.create_spot_release_service(conn)

        db_user_id = user_service.get_db_user_id_by_tg_id(tg_user_id)
        if not db_user_id:
            return None

        release: RevokeRelease = spot_release_service.get_release_for_confirm_revoke(
            db_user_id=db_user_id,
            release_id=release_id
        )

        if release.status == ParkingReleaseStatus.ACCEPTED:
            await callback.message.edit_text(
                text="⚠️ Место уже кому-то отдано",
                reply_markup=back_to_revoke_release_markup
            )
            return None
        elif release.status == ParkingReleaseStatus.WAITING:
            await callback.message.edit_text(
                text="⚠️ Место уже кому-то предложили",
                reply_markup=back_to_revoke_release_markup
            )
            return None

        spot_release_service.update_parking_release_set_free(
            release_id=release_id,
            current_status=ParkingReleaseStatus.CANCELED
        )

        conn.commit()

        message_text = (f"Вы успешно отозвали место <b>№{release.spot_id} </b>"
                        f"на дату <u>{release.release_date.strftime('%d.%m.%Y')}</u>\n\n"
                        f"ℹ️ <i>Это больше не будет назначаться никому в эту дату</i>")

        user_name = await get_user_full_mention(tg_user_id, False)
        await log(
            log_type=LogType.INFO,
            log_message=f"{user_name} отозвал место №{release.spot_id} "
                        f"на дату {release.release_date.strftime('%d.%m.%Y')}"
        )

        await callback.message.edit_text(
            text=message_text,
            reply_markup=back_to_revoke_release_markup
        )

    return None
