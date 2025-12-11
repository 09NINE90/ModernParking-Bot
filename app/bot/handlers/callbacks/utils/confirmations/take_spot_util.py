from datetime import datetime

from aiogram.types import CallbackQuery

from app.bot.keyboards import back_to_main_markup
from app.bot.notification.edit_message import edit_message
from app.bot.notification.messages import to_owner_message
from app.bot.notification.notify_user import notify_user
from app.bot.utils import get_user_full_mention
from app.data import get_db_connection
from app.data.models import SpotConfirmationDTO, ParkingRequestStatus, ConfirmationStatus
from app.logs.log_builder import log, LogType
from app.services import ServiceFactory
from app.utils.daily_statistics_util import update_daily_statistics_by_date


async def take_spot(callback: CallbackQuery):
    """
        Подтверждает занятие парковочного места пользователем.
        Логика:
        - ищем своё WAITING-подтверждение;
        - пытаемся атомарно занять место (accept_spot_if_free);
        - если не успели — помечаем свои подтверждения как CANCELLED и показываем ошибку;
        - если успели — ставим:
            * свой request -> ACCEPTED,
            * своё confirmation -> ACCEPTED,
            * остальные WAITING по этому release -> CANCELLED + их request -> PENDING + редактируем сообщения.
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
            await callback.message.edit_text(
                text="⚠️ Это место уже недоступно.",
                reply_markup=back_to_main_markup
            )
            return None

        spot_confirmation_data = get_spot_confirmation_data_from_result(result)

        updated = spot_release_service.accept_spot_if_free(
            release_id=spot_confirmation_data.release_id,
            user_id=db_user_id
        )
        if not updated:
            spot_confirmation_service.set_status(
                spot_confirmation_id=spot_confirmation_data.confirmation_id,
                status=ConfirmationStatus.CANCELLED
            )
            await callback.message.edit_text(
                "⚠️ К сожалению, это место уже занял другой пользователь.",
                reply_markup=back_to_main_markup
            )
            conn.commit()
            return None

        # Если сюда дошли — место наше

        # 1. Обновляем статус своего запроса
        spot_request_service.update_parking_request_status(
            request_id=spot_confirmation_data.request_id,
            current_status=ParkingRequestStatus.ACCEPTED
        )

        # 2. Обновляем статус своего подтверждения
        spot_confirmation_service.set_status(
            spot_confirmation_id=spot_confirmation_data.confirmation_id,
            status=ConfirmationStatus.ACCEPTED
        )

        # 3. Обрабатываем всех остальных кандидатов по этому релизу
        losers = spot_confirmation_service.get_waiting_confirmations_by_release_except_user(
            release_id=spot_confirmation_data.release_id,
            user_id=db_user_id
        )

        # Для каждого проигравшего:
        # - вернуть request в PENDING
        # - пометить confirmation как CANCELLED
        # - отредактировать сообщение
        for loser_id, loser_user_id, loser_request_id, loser_message_id, loser_tg_id in losers:
            # вернуть запрос в очередь
            spot_request_service.update_parking_request_status(
                request_id=loser_request_id,
                current_status=ParkingRequestStatus.PENDING
            )

            # статус подтверждения -> CANCELLED
            spot_confirmation_service.set_status(
                spot_confirmation_id=loser_id,
                status=ConfirmationStatus.CANCELLED
            )

            await edit_message(
                tg_chat_id=loser_tg_id,
                editing_message_id=loser_message_id,
                new_message_text="Вам было предложено место на сегодня."
                                 " Но другой пользователь успел занять его раньше😔\n\n"
                                 "<i>ℹ️ Ваша заявка возвращена в очередь.</i>",
            )

        # 4. Прокачиваем рейтинг пользователя
        user_service.update_user_rating_by_user_id(
            db_user_id=db_user_id,
            delta=1,
            user_name=user_name
        )

        # 5. Уведомляем владельца релиза
        await notify_release_owner(spot_release_service, spot_confirmation_data)

        request_status = spot_request_service.get_request_status_by_id(spot_confirmation_data.request_id)
        release_status = spot_release_service.get_release_status_by_id(spot_confirmation_data.release_id)

        conn.commit()

        user_name = await get_user_full_mention(tg_user_id, False)

        await callback.message.edit_text(
            text=(
                f"✅ Вы успешно заняли место №{spot_confirmation_data.spot_number} "
                f"на {spot_confirmation_data.assignment_date.strftime('%d.%m.%Y')}"
            ),
            reply_markup=back_to_main_markup
        )
        await log(
            log_type=LogType.INFO,
            log_message=(
                f"{user_name} успешно занял место №{spot_confirmation_data.spot_number}\n"
                f"release_status = {release_status}\n"
                f"request_status = {request_status}"
            )
        )

        datetime_now = datetime.now()
        await update_daily_statistics_by_date(datetime_now)

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


async def notify_release_owner(spot_release_service, spot_confirmation_data):
    release_owner = spot_release_service.get_release_owner(
        release_id=spot_confirmation_data.release_id,
    )
    if release_owner:
        release_user_id, release_tg_id = release_owner
        message_text = await to_owner_message(
            tg_user_id=release_tg_id,
            spot_number=spot_confirmation_data.spot_number,
            assignment_date=spot_confirmation_data.assignment_date
        )
        await notify_user(release_tg_id, message_text)
