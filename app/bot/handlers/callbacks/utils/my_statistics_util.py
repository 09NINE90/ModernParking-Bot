from datetime import datetime

from aiogram.types import CallbackQuery

from app.bot.keyboards.inline.base import return_to_main_markup
from app.config import settings
from app.data import get_db_connection
from app.services import ServiceFactory


async def get_my_statistics(callback: CallbackQuery):
    if callback.message.chat.id == settings.GROUP_ID:
        return None

    today = datetime.now()
    tg_user_id = callback.from_user.id

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)
        spot_release_service = ServiceFactory.create_spot_release_service(conn)
        spot_request_service = ServiceFactory.create_spot_request_service(conn)
        statistics_service = ServiceFactory.create_statistics_service(conn)

        db_user_id = user_service.get_db_user_id_by_tg_id(tg_user_id)
        if not db_user_id:
            return None

        request_statistics = statistics_service.get_user_request_statistics(db_user_id)
        release_statistics = statistics_service.get_user_release_statistics(db_user_id)

        current_spots_requests = spot_request_service.get_current_spots_request_by_user(
            user_id=db_user_id,
            rq_date=today.date()
        )
        current_spots_releases = spot_release_service.get_current_spots_releases_by_user(
            user_id=db_user_id,
            rq_date=today.date()
        )

        message_text = get_start_message_text(request_statistics, release_statistics)

        message_text = update_message_text_by_request(message_text, current_spots_requests)
        message_text = update_message_text_by_releases(message_text, current_spots_releases)

        await callback.message.edit_text(
            text=message_text,
            reply_markup=return_to_main_markup
        )

        return None


def get_start_message_text(request_statistics, release_statistics):
    return (
        f"<b>Ваша статистика за всё время:</b>\n\n"
        f"<b>Запросы мест:</b>\n"
        f"┌ 🧮 Всего запросов: <b>{request_statistics['total_user_requests']}</b>\n"
        f"├ ✅ Успешные бронирования: <b>{request_statistics['accepted_spots_count']}</b>\n"
        f"├ 🤷 Не нашлось мест по запросу: <b>{request_statistics['not_found_spots_count']}</b>\n"
        f"└ ❌ Отменённые запросы: <b>{request_statistics['canceled_spots_count']}</b>\n\n"
        f"<b>Освобождение мест:</b>\n"
        f"┌ 🧮 Всего освобождено мест: <b>{release_statistics['total_user_releases']}</b>\n"
        f"├ ✅ Мест приняли: <b>{release_statistics['accepted_releases_count']}</b>\n"
        f"├ 🤷 Никто не взял: <b>{release_statistics['not_found_releases_count']}</b>\n"
        f"└ ❌ Отозвано мест: <b>{release_statistics['canceled_releases_count']}</b>\n\n"
    )


def update_message_text_by_request(message_text, current_spots_requests):
    if len(current_spots_requests) > 0:
        message_text += "\n<b>Ваши актуальные запросы на парковочные места:</b>\n"
        for current_spot in current_spots_requests:
            spot_info = ""
            if current_spot.spot_id:
                spot_info = f" <b>№{current_spot.spot_id}</b>"
            emoji_status = current_spot.status.emoji
            message_text += (f"📅 Дата: {current_spot.request_date.strftime('%d.%m.%Y')}\n"
                             f"{emoji_status} Статус: {current_spot.status.display_name}{spot_info}\n\n")
    else:
        message_text += "\nУ Вас пока что нет актуальных запросов на парковочные места\n"

    return message_text


def update_message_text_by_releases(message_text, current_spots_releases):
    if len(current_spots_releases) > 0:
        message_text += "\n<b>Ваши актуальные освобожденные парковочные места:</b>\n"
        for current_spot in current_spots_releases:
            emoji_status = current_spot.status.emoji
            message_text += (f"📅 Дата: {current_spot.release_date.strftime('%d.%m.%Y')}\n"
                             f"📍 Место: №{current_spot.spot_id}\n"
                             f"{emoji_status} Статус: {current_spot.status.display_name}\n\n")
    else:
        message_text += "\nУ Вас пока что нет актуальных освобожденных парковочных мест\n"

    return message_text
