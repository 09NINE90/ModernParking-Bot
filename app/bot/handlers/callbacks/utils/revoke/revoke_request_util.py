from datetime import date

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.handlers.callbacks.utils.distribution_spots_util import distribute_parking_spots
from app.bot.keyboards import back_to_main_markup
from app.bot.keyboards.inline import revoke_requests_markup, confirmation_revoke_requests_markup, \
    back_to_revoke_request_markup
from app.bot.utils import get_user_full_mention
from app.data import get_db_connection
from app.data.models import RevokeRequest, ParkingRequestStatus, ParkingReleaseStatus
from app.logs.log_builder import log, LogType
from app.services import ServiceFactory


async def choose_request_for_revocation(callback: CallbackQuery, state: FSMContext):
    today = date.today()
    tg_user_id = callback.from_user.id

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)
        spot_request_service = ServiceFactory.create_spot_request_service(conn)

        db_user_id = user_service.get_db_user_id_by_tg_id(tg_user_id)
        if not db_user_id:
            return None

        requests_for_revoke = spot_request_service.get_user_requests_for_revoke(db_user_id, today)
        if not requests_for_revoke:
            await callback.message.edit_text(
                text="Не найдено актуальных дат для отмены бронирования места",
                reply_markup=back_to_main_markup
            )
            return None

        message_text = f"Список дат, на которые вы запрашивали места от <u>{today.strftime('%d.%m.%Y')}</u>:"
        markup = revoke_requests_markup(requests_for_revoke)
        await callback.message.edit_text(
            text=message_text,
            reply_markup=markup
        )

    return None


async def confirmation_revoke_request(callback: CallbackQuery, request_id):
    tg_user_id = callback.from_user.id

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)
        spot_request_service = ServiceFactory.create_spot_request_service(conn)

        db_user_id = user_service.get_db_user_id_by_tg_id(tg_user_id)
        if not db_user_id:
            return None

        request: RevokeRequest = spot_request_service.get_request_for_confirm_revoke(db_user_id, request_id)
        if request.spot_id is None:
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

        await callback.message.edit_text(
            text=message_text,
            reply_markup=confirmation_revoke_requests_markup(request, markup_text)
        )

    return None


async def confirm_revoke_request(callback: CallbackQuery, request_id):
    tg_user_id = callback.from_user.id
    user_name = await get_user_full_mention(tg_user_id, False)

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)
        spot_request_service = ServiceFactory.create_spot_request_service(conn)
        spot_release_service = ServiceFactory.create_spot_release_service(conn)

        db_user_id = user_service.get_db_user_id_by_tg_id(tg_user_id)
        if not db_user_id:
            return None

        request: RevokeRequest = spot_request_service.get_request_for_confirm_revoke(db_user_id, request_id)
        if request.spot_id is None:
            spot_request_service.update_parking_request_status(
                request_id=request_id,
                current_status=ParkingRequestStatus.CANCELED
            )

            message_text = (f"Вы успешно отозвали запрос на парковочное место "
                            f"на дату <u>{request.request_date.strftime('%d.%m.%Y')}</u>")

        else:
            spot_release_service.update_parking_release_set_free(
                release_id=request.release_id,
                current_status=ParkingReleaseStatus.PENDING
            )
            spot_request_service.update_parking_request_status(
                request_id=request_id,
                current_status=ParkingRequestStatus.CANCELED
            )
            user_service.update_user_rating_by_user_id(
                db_user_id=db_user_id,
                delta=-1,
                user_name=user_name
            )
            message_text = (f"Вы успешно отказались от парковочного места <b>№{request.spot_id}</b> "
                            f"на дату <u>{request.request_date.strftime('%d.%m.%Y')}</u>\n\n"
                            f"ℹ️ <i>Это место будет предложено кому-нибудь другому</i>")

            await log(
                log_type=LogType.INFO,
                log_message=f"{user_name} отказался от парковочного места №{request.spot_id} "
                            f"на дату {request.request_date.strftime('%d.%m.%Y')}"
            )

        conn.commit()

        await distribute_parking_spots()

        await callback.message.edit_text(
            text=message_text,
            reply_markup=back_to_revoke_request_markup
        )

    return None
