from datetime import datetime

from aiogram.types import CallbackQuery

from app.bot.keyboards import back_to_main_markup
from app.bot.utils import get_user_full_mention
from app.data import get_db_connection
from app.data.models import SpotConfirmationDTO, ParkingRequestStatus, ConfirmationStatus, ParkingReleaseStatus
from app.logs.log_builder import log, LogType
from app.services import ServiceFactory
from app.utils.daily_statistics_util import update_daily_statistics_by_date


async def cancel_spot(callback: CallbackQuery):
    """
        Обрабатывает отмену занятия места пользователем.
        Логика:
        - находим своё WAITING-подтверждение;
        - помечаем request как CANCELED;
        - помечаем confirmation как REJECTED;
        - редактируем сообщение пользователю;
        - логируем и обновляем статистику.
    """
    tg_user_id = callback.from_user.id
    user_name = await get_user_full_mention(tg_user_id, False)

    with get_db_connection() as conn:

        user_service = ServiceFactory.create_user_service(conn)
        spot_release_service = ServiceFactory.create_spot_release_service(conn)
        spot_request_service = ServiceFactory.create_spot_request_service(conn)
        spot_confirmation_service = ServiceFactory.create_spot_confirmation_service(conn)

        db_user_id = user_service.get_db_user_id_by_tg_id(tg_user_id)
        if not db_user_id:
            return None

        result = spot_confirmation_service.get_spot_confirmation(db_user_id)
        if not result:
            return None

        spot_confirmation_data = get_spot_confirmation_data_from_result(result)

        # 1. Помечаем заявку как CANCELED
        spot_request_service.update_parking_request_status(
            request_id=spot_confirmation_data.request_id,
            current_status=ParkingRequestStatus.CANCELED
        )

        # 2. Статус подтверждения -> REJECTED
        spot_confirmation_service.set_status(
            spot_confirmation_id=spot_confirmation_data.confirmation_id,
            status=ConfirmationStatus.REJECTED
        )

        # 2.1. Если больше нет WAITING по этому релизу — возвращаем релиз в PENDING
        has_waiting = spot_confirmation_service.has_waiting_confirmations_for_release(
            release_id=spot_confirmation_data.release_id
        )
        if not has_waiting:
            spot_release_service.update_release_status(
                release_id=spot_confirmation_data.release_id,
                current_status=ParkingReleaseStatus.PENDING
            )

        request_status = spot_request_service.get_request_status_by_id(spot_confirmation_data.request_id)
        release_status = spot_release_service.get_release_status_by_id(spot_confirmation_data.release_id)

        conn.commit()

        await callback.message.edit_text(
            text=(
                f"ℹ️ Вы успешно отказались от места №{spot_confirmation_data.spot_number} "
                f"на {spot_confirmation_data.assignment_date.strftime('%d.%m.%Y')}\n\n"
                "️️⚠️ <i>Я больше не буду предлагать вам места на эту дату</i>"
            ),
            reply_markup=back_to_main_markup
        )

        datetime_now = datetime.now()
        await update_daily_statistics_by_date(datetime_now)

        await log(
            log_type=LogType.INFO,
            log_message=(
                f"{user_name} отказался от места №{spot_confirmation_data.spot_number}\n"
                f"release_status = {release_status}\n"
                f"request_status = {request_status}"
            )
        )

        return None


def get_spot_confirmation_data_from_result(result):
    return SpotConfirmationDTO(
        confirmation_id=result[0],
        db_user_id=result[1],
        tg_user_id=result[2],
        spot_number=result[3],
        assignment_date=result[4],
        release_id=result[5],
        request_id=result[6],
        message_sent_id=result[7],
    )
