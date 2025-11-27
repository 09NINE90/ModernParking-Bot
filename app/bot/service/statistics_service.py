import logging
from datetime import datetime, timedelta

import psycopg2
from aiogram import types
from aiogram.types import CallbackQuery

from app.bot.config import GROUP_ID, LOGS_CHANNEL_ID
from app.bot.constants.car_emojis import get_random_car_emoji
from app.bot.constants.emoji_status import get_request_emoji_status, get_release_emoji_status
from app.bot.constants.log_types import LogNotification
from app.bot.notification.daily_statistics_notification import daily_statistics_notification
from app.bot.notification.log_notification import send_log_notification
from app.bot.notification.send_user_statistics import send_user_statistics
from app.bot.notification.weeky_statistics_notification import weekly_statistics_notification
from app.bot.service.user_service import get_db_user_id
from app.bot.users.get_user_full_mention import get_user_full_mention
from app.data.init_db import get_db_connection
from app.data.models.releases.parking_releases import ParkingReleaseStatus, ParkingRelease
from app.data.models.requests.parking_requests import ParkingRequestStatus, ParkingRequest
from app.data.models.parking_transfers_dto import ParkingTransfer
from app.data.repository.parking_releases_repository import free_parking_releases_by_date, \
    parking_releases_between_two_dates, current_spots_releases_by_user, get_parking_releases_statistics_for_period
from app.data.repository.parking_requests_repository import parking_requests_between_two_dates, \
    all_parking_requests_by_status_and_user, current_spots_request_by_user, get_parking_requests_statistics_for_period
from app.data.repository.statistics_repository import get_parking_transfers_by_date, get_parking_transfers_by_week
from app.log_text import USER_STATISTICS_ERROR, WEEKLY_STATISTICS_SERVICE_ERROR, DAILY_STATISTICS_SERVICE_ERROR, \
    DB_USER_ID_GET_ERROR, DATABASE_ERROR


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
                        recipient = await get_user_full_mention(user_id=transfer.recipient_tg_id, is_link=True)
                        owner = await get_user_full_mention(user_id=transfer.owner_tg_id, is_link=True)
                        spot = transfer.spot_id
                        message_text += f"{emoji} {owner} отдал место <b>№{spot}</b> -> {recipient}\n\n"

                    await daily_statistics_notification(tg_chat_id=GROUP_ID, message=message_text,
                                                        assignment_date=day.date(), is_pinned=True)
                    await daily_statistics_notification(tg_chat_id=LOGS_CHANNEL_ID, message=message_text,
                                                        assignment_date=day.date())
                else:
                    message_text += "👀Трансферов мест пока не было..."
                    await daily_statistics_notification(tg_chat_id=GROUP_ID, message=message_text,
                                                        assignment_date=day.date(), is_pinned=True)
                    await daily_statistics_notification(tg_chat_id=LOGS_CHANNEL_ID, message=message_text,
                                                        assignment_date=day.date())
    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))
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
                accepted_parking_releases = await parking_releases_between_two_dates(cur, ParkingReleaseStatus.ACCEPTED.name,
                                                                           monday_date.date(), friday_date.date())
                accepted_spots_count = len(accepted_parking_releases)

                not_found_parking_requests = await parking_requests_between_two_dates(cur, ParkingRequestStatus.NOT_FOUND.name,
                                                                            monday_date.date(), friday_date.date())
                not_found_spots_count = len(not_found_parking_requests)

                canceled_parking_requests = await parking_requests_between_two_dates(cur, ParkingRequestStatus.CANCELED.name,
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
                        recipient = await get_user_full_mention(user_id=transfer.recipient_tg_id, is_link=True)
                        owner = await get_user_full_mention(user_id=transfer.owner_tg_id, is_link=True)
                        spot = transfer.spot_id
                        message_text += f"{emoji} {owner} отдал место <b>№{spot}</b> -> {recipient}\n\n"

                    await weekly_statistics_notification(tg_chat_id=GROUP_ID, message=message_text,
                                                         monday_date=monday_date.date(), friday_date=friday_date.date(),
                                                         is_pinned=True)
                    await weekly_statistics_notification(tg_chat_id=LOGS_CHANNEL_ID, message=message_text,
                                                         monday_date=monday_date.date(), friday_date=friday_date.date())
                else:
                    message_text += "👀Трансферов мест пока не было..."
                    await weekly_statistics_notification(tg_chat_id=GROUP_ID, message=message_text,
                                                         monday_date=monday_date.date(), friday_date=friday_date.date(),
                                                         is_pinned=True)
                    await weekly_statistics_notification(tg_chat_id=LOGS_CHANNEL_ID, message=message_text,
                                                         monday_date=monday_date.date(), friday_date=friday_date.date())
    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))
    except Exception as e:
        logging.error(WEEKLY_STATISTICS_SERVICE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, WEEKLY_STATISTICS_SERVICE_ERROR.format(e))


async def my_statistics(query: CallbackQuery):
    """
        Асинхронная служба для формирования и отправки статистики пользователю по парковочным местам.
    """
    try:
        today = datetime.now()
        tg_user_id = query.from_user.id

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                db_user_id = await get_db_user_id(cur, tg_user_id)

                if not db_user_id:
                    logging.error(DB_USER_ID_GET_ERROR.format(tg_user_id))
                    await send_log_notification(LogNotification.ERROR, DB_USER_ID_GET_ERROR.format(tg_user_id))
                    return None

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
                current_spots_request = [ParkingRequest(status=row[0], request_date=row[1], spot_id=row[2])
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
                        spot_info = ""
                        if current_spot.spot_id:
                            spot_info = f" <b>№{current_spot.spot_id}</b>"
                        emoji_status = await get_request_emoji_status(current_spot.status)
                        message_text += (f"📅 Дата: {current_spot.request_date.strftime('%d.%m.%Y')}\n"
                                         f"{emoji_status} Статус: {current_spot.status.display_name}{spot_info}\n\n")
                else:
                    message_text += "\nУ вас пока что нет актуальных запросов на парковочные места\n"

                if len(current_spots_releases) > 0:
                    message_text += "\n<b>Ваши актуальные освобожденные парковочные места:</b>\n"
                    for current_spot in current_spots_releases:
                        emoji_status = await get_release_emoji_status(current_spot.status)
                        message_text += (f"📅 Дата: {current_spot.release_date.strftime('%d.%m.%Y')}\n"
                                         f"📍 Место: №{current_spot.spot_id}\n"
                                         f"{emoji_status} Статус: {current_spot.status.display_name}\n\n")
                else:
                    message_text += "\nУ вас пока что нет актуальных освобожденных парковочных мест\n"

                await send_user_statistics(query, message_text)
    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))
    except Exception as e:
        logging.error(USER_STATISTICS_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, USER_STATISTICS_ERROR.format(e))

async def for_admin_statistics(message: types.Message):
    try:
        today = datetime.now()
        last_day = today
        first_day = today - timedelta(days=30)
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                releases_stats = await get_parking_releases_statistics_for_period(cur, first_day, last_day)

                requests_stats = await get_parking_requests_statistics_for_period(cur, first_day, last_day)

                message_text = (
                    f"📊 <b>Статистика парковок за 30 дней</b>\n\n"
                    f"<i>Период: {first_day.strftime('%d.%m.%Y')} - {last_day.strftime('%d.%m.%Y')}</i>\n\n"

                    f"<b>Освобождение мест:</b>\n"
                    f"• Мест отдано: <b>{releases_stats['accepted']}</b>\n"
                    f"• Ожидание распределения: <b>{releases_stats['pending']}</b>\n"
                    f"• Отозвали мест: <b>{releases_stats['canceled']}</b>\n"
                    f"• Не нашлось, кому отдать: <b>{releases_stats['not_found']}</b>\n"
                    f"• Ожидание подтверждения: <b>{releases_stats['waiting']}</b>\n"
                    f"• Всего освобождено: <b>{releases_stats['total']}</b>\n\n"

                    f"<b>Запросы мест:</b>\n"
                    f"• Мест принято: <b>{requests_stats['accepted']}</b>\n"
                    f"• Ожидание распределения: <b>{requests_stats['pending']}</b>\n"
                    f"• Отозвали запрос: <b>{requests_stats['canceled']}</b>\n"
                    f"• Не найдено мест: <b>{requests_stats['not_found']}</b>\n"
                    f"• Ожидание подтверждения: <b>{requests_stats['waiting_confirmation']}</b>\n"
                    f"• Всего запросов: <b>{requests_stats['total']}</b>"
                )

                await message.answer(message_text)

    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))