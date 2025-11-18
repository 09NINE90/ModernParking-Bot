import logging
from datetime import datetime, timedelta

from aiogram.types import CallbackQuery

from app.bot.config import GROUP_ID, CHANNEL_ID
from app.bot.constants.car_emojis import get_random_car_emoji
from app.bot.constants.emoji_status import get_request_emoji_status, get_release_emoji_status
from app.bot.constants.log_types import LogNotification
from app.bot.notification.daily_statistics_notification import daily_statistics_notification
from app.bot.notification.log_notification import send_log_notification
from app.bot.notification.send_user_statistics import send_user_statistics
from app.bot.notification.weeky_statistics_notification import weekly_statistics_notification
from app.bot.users.get_user_full_mention import get_user_full_mention
from app.data.init_db import get_db_connection
from app.data.models.parking_releases import ParkingReleaseStatus, ParkingRelease
from app.data.models.parking_requests import ParkingRequestStatus, ParkingRequest
from app.data.models.parking_transfers import ParkingTransfer
from app.data.repository.parking_releases_repository import free_parking_releases_by_date, \
    parking_releases_by_week, current_spots_releases_by_user
from app.data.repository.parking_requests_repository import parking_requests_by_week, \
    all_parking_requests_by_status_and_user, current_spots_request_by_user
from app.data.repository.statistics_repository import get_parking_transfers_by_date, get_parking_transfers_by_week
from app.data.repository.users_repository import get_user_id_by_tg_id
from app.log_text import USER_STATISTICS_ERROR, WEEKLY_STATISTICS_SERVICE_ERROR, DAILY_STATISTICS_SERVICE_ERROR


async def daily_statistics_service(plus_day=0):
    """
        Асинхронная служба для формирования и отправки ежедневной статистики по парковочным местам.
    """
    try:
        day = datetime.today() + timedelta(days=plus_day)
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                free_parking_releases = await free_parking_releases_by_date(cur, day.date())
                free_spots = len(free_parking_releases)

                results = await get_parking_transfers_by_date(cur, day.date())
                transfers = [ParkingTransfer(spot_id=row[0], recipient_tg_id=row[1], owner_tg_id=row[2])
                             for row in results]

                message_text = f"\nСвободных мест всего: <b>{free_spots}</b>\n"
                if len(transfers) > 0:
                    message_text += "\n<b>Трансферы мест:</b>\n"
                    for transfer in transfers:
                        emoji = get_random_car_emoji()
                        recipient = await get_user_full_mention(transfer.recipient_tg_id)
                        owner = await get_user_full_mention(transfer.owner_tg_id)
                        spot = transfer.spot_id
                        message_text += f"{emoji} {owner} отдал место <b>№{spot}</b> -> {recipient}\n\n"

                    await daily_statistics_notification(tg_chat_id=GROUP_ID, message=message_text,
                                                        assignment_date=day.date())
                    await daily_statistics_notification(tg_chat_id=CHANNEL_ID, message=message_text,
                                                        assignment_date=day.date())
                else:
                    message_text += "👀Трансферов мест пока не было..."
                    await daily_statistics_notification(tg_chat_id=GROUP_ID, message=message_text,
                                                        assignment_date=day.date())
                    await daily_statistics_notification(tg_chat_id=CHANNEL_ID, message=message_text,
                                                        assignment_date=day.date())
    except Exception as e:
        logging.error(DAILY_STATISTICS_SERVICE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DAILY_STATISTICS_SERVICE_ERROR.format(e))


async def weekly_statistics_service():
    """
        Асинхронная служба для формирования и отправки еженедельной статистики по парковочным местам.
    """
    try:
        today = datetime.now()
        monday_date = today - timedelta(days=today.weekday())
        friday_date = monday_date + timedelta(days=4)
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                accepted_parking_releases = await parking_releases_by_week(cur, ParkingReleaseStatus.ACCEPTED.name,
                                                                           monday_date.date(), friday_date.date())
                accepted_spots_count = len(accepted_parking_releases)

                not_found_parking_requests = await parking_requests_by_week(cur, ParkingRequestStatus.NOT_FOUND.name,
                                                                            monday_date.date(), friday_date.date())
                not_found_spots_count = len(not_found_parking_requests)

                canceled_parking_requests = await parking_requests_by_week(cur, ParkingRequestStatus.CANCELED.name,
                                                                           monday_date.date(), friday_date.date())
                canceled_spots_count = len(canceled_parking_requests)

                results = await get_parking_transfers_by_week(cur, monday_date.date(), friday_date.date())
                transfers = [ParkingTransfer(spot_id=row[0], recipient_tg_id=row[1], owner_tg_id=row[2])
                             for row in results]

                message_text = (f"\n✅ Реализовано мест всего: <b>{accepted_spots_count}</b>\n"
                                f"🤷‍♂️ Не найдено мест по запросу: <b>{not_found_spots_count}</b>\n"
                                f"❌ Отклонено мест: <b>{canceled_spots_count}</b>\n")
                if len(transfers) > 0:
                    message_text += "\n<b>Трансферы мест:</b>\n"
                    for transfer in transfers:
                        emoji = get_random_car_emoji()
                        recipient = await get_user_full_mention(transfer.recipient_tg_id)
                        owner = await get_user_full_mention(transfer.owner_tg_id)
                        spot = transfer.spot_id
                        message_text += f"{emoji} {owner} отдал место <b>№{spot}</b> -> {recipient}\n\n"

                    await weekly_statistics_notification(tg_chat_id=GROUP_ID, message=message_text,
                                                         monday_date=monday_date.date(), friday_date=friday_date.date())
                    await weekly_statistics_notification(tg_chat_id=CHANNEL_ID, message=message_text,
                                                         monday_date=monday_date.date(), friday_date=friday_date.date())
                else:
                    message_text += "👀Трансферов мест пока не было..."
                    await weekly_statistics_notification(tg_chat_id=GROUP_ID, message=message_text,
                                                         monday_date=monday_date.date(), friday_date=friday_date.date())
                    await weekly_statistics_notification(tg_chat_id=CHANNEL_ID, message=message_text,
                                                         monday_date=monday_date.date(), friday_date=friday_date.date())
    except Exception as e:
        logging.error(WEEKLY_STATISTICS_SERVICE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, WEEKLY_STATISTICS_SERVICE_ERROR.format(e))


async def my_statistics(query: CallbackQuery):
    """
        Асинхронная служба для формирования и отправки статистики пользователю по парковочным местам.
    """
    try:
        today = datetime.now()
        user_tg_id = query.from_user.id

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                user_record = await get_user_id_by_tg_id(cur, user_tg_id)

                if not user_record:
                    await query.message.answer("❌ Ошибка: пользователь не найден")
                    return None

                db_user_id = user_record[0]

                not_found_spots = await all_parking_requests_by_status_and_user(cur, ParkingRequestStatus.NOT_FOUND.name,
                                                                                db_user_id)
                not_found_spots_count = len(not_found_spots)

                canceled_parking_requests = await all_parking_requests_by_status_and_user(cur,
                                                                                          ParkingRequestStatus.CANCELED.name,
                                                                                          db_user_id)
                canceled_spots_count = len(canceled_parking_requests)

                accepted_parking_requests = await all_parking_requests_by_status_and_user(cur,
                                                                                          ParkingRequestStatus.ACCEPTED.name,
                                                                                          db_user_id)
                accepted_spots_count = len(accepted_parking_requests)

                results = await current_spots_request_by_user(cur, db_user_id, today.date())
                current_spots_request = [ParkingRequest(status=row[0], request_date=row[1])
                                         for row in results]

                results = await current_spots_releases_by_user(cur, db_user_id, today.date())
                current_spots_releases = [ParkingRelease(spot_id=row[0], status=row[1], release_date=row[2])
                                          for row in results]

                message_text = (f"<b>Ваша статистика за всё время:</b>\n"
                                f"┌ ✅ Успешные бронирования: <b>{accepted_spots_count}</b>\n"
                                f"├ 🤷 Не нашлось мест по запросу: <b>{not_found_spots_count}</b>\n"
                                f"└ ❌ Отменённые запросы: <b>{canceled_spots_count}</b>\n")

                if len(current_spots_request) > 0:
                    message_text += "\n<b>Ваши актуальные запросы на парковочные места:</b>\n"
                    for current_spot in current_spots_request:
                        emoji_status = await get_request_emoji_status(current_spot.status)
                        message_text += (f"📅 Дата: {current_spot.request_date.strftime('%d.%m.%Y')}\n"
                                         f"{emoji_status} Статус: {current_spot.status.display_name}\n\n")
                else:
                    message_text += "\nУ вас пока что нет актуальных запросов на парковочные места"

                if len(current_spots_releases) > 0:
                    message_text += "\n<b>Ваши актуальные освобожденные парковочные места:</b>\n"
                    for current_spot in current_spots_releases:
                        emoji_status = await get_release_emoji_status(current_spot.status)
                        message_text += (f"📅 Дата: {current_spot.release_date.strftime('%d.%m.%Y')}\n"
                                         f"📍 Место: №{current_spot.spot_id}\n"
                                         f"{emoji_status} Статус: {current_spot.status.display_name}\n\n")
                else:
                    message_text += "\nУ вас пока что нет актуальных освобожденных парковочных мест"

                await send_user_statistics(query, message_text)
    except Exception as e:
        logging.error(USER_STATISTICS_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, USER_STATISTICS_ERROR.format(e))