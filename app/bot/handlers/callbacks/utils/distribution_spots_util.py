import random
from datetime import datetime

from app.bot.notification.enumz import NotificationTypes
from app.bot.notification.messages import to_user_about_assigned_spot, to_user_about_found_spot, to_owner_message
from app.bot.notification.notify_user import notify_user
from app.bot.utils import get_user_full_mention
from app.data import get_db_connection
from app.data.models import ParkingReleaseStatus, ParkingRequestStatus, SpotConfirmationDTO
from app.logs.log_builder import log, LogType
from app.services import ServiceFactory
from app.utils.daily_statistics_util import update_daily_statistics_by_date


async def distribute_parking_spots():
    await log(
        log_type=LogType.DEBUG,
        log_message=f"Начато распределение парковочных мест",
        is_sending_log=False
    )
    today_date = datetime.today().date()
    datetime_now = datetime.now()
    today_8_30am = datetime_now.replace(hour=8, minute=30, second=0, microsecond=0)
    try:
        with get_db_connection() as conn:
            distributed_count = 0
            waiting_count = 0
            release_notifications = []

            user_service = ServiceFactory.create_user_service(conn)
            spot_release_service = ServiceFactory.create_spot_release_service(conn)
            spot_request_service = ServiceFactory.create_spot_request_service(conn)
            spot_confirmation_service = ServiceFactory.create_spot_confirmation_service(conn)

            dates_with_availability = spot_release_service.get_dates_with_availability()
            if not dates_with_availability:
                await log(
                    log_type=LogType.INFO,
                    log_message=f"Нет мест для распределения",
                    is_sending_log=False
                )
                return None

            for distribution_date in dates_with_availability:

                free_spots = spot_release_service.get_free_spots_by_date(distribution_date)
                if not free_spots:
                    await log(
                        log_type=LogType.DEBUG,
                        log_message="Не найдено свободных мест на дату "
                                    f"{distribution_date.strftime('%d.%m.%Y')}",
                        is_sending_log=False
                    )
                    continue

                candidates = spot_request_service.get_spot_candidates(distribution_date, len(free_spots))
                if not candidates:
                    await log(
                        log_type=LogType.DEBUG,
                        log_message="Не найдены кандидаты на место на дату "
                                    f"{distribution_date.strftime('%d.%m.%Y')}",
                        is_sending_log=False
                    )
                    continue

                min_rating = candidates[0][2]
                min_rating_candidates = [c for c in candidates if c[2] == min_rating]
                random.shuffle(min_rating_candidates)
                selected_candidates = min_rating_candidates[:len(free_spots)]

                for i, (request_id, user_id, current_rating, tg_id) in enumerate(selected_candidates):
                    release_id, spot_id = free_spots[i]
                    user_name = await get_user_full_mention(tg_id)

                    if not spot_release_service.is_spot_still_available(release_id):
                        request_status = spot_request_service.get_request_status_by_id(request_id)
                        release_status = spot_release_service.get_release_status_by_id(release_id)
                        await log(
                            log_type=LogType.WARN,
                            log_message=(
                                f"Spot {spot_id} no longer available, skipping\n"
                                f"release_status = {release_status}\n"
                                f"request_status = {request_status}"
                            )
                        )
                        continue

                    if (distribution_date == today_date) and (datetime_now > today_8_30am):
                        spot_release_service.update_parking_releases(
                            user_id=user_id,
                            release_id=release_id,
                            current_status=ParkingReleaseStatus.WAITING
                        )
                        spot_request_service.update_parking_request_status(
                            request_id=request_id,
                            current_status=ParkingRequestStatus.WAITING_CONFIRMATION
                        )

                        spot_confirmation_data = SpotConfirmationDTO(
                            db_user_id=str(user_id),
                            tg_user_id=tg_id,
                            spot_number=spot_id,
                            assignment_date=distribution_date,
                            release_id=release_id,
                            request_id=request_id
                        )

                        spot_confirmation_id = spot_confirmation_service.create_spot_confirmation(
                            spot_confirmation_data)

                        message_text = await to_user_about_found_spot(spot_confirmation_data)
                        message_id = await notify_user(tg_id, message_text, NotificationTypes.SPOT_FOUND)

                        spot_confirmation_service.set_message_sent_id(spot_confirmation_id, message_id)

                        request_status = spot_request_service.get_request_status_by_id(request_id)
                        release_status = spot_release_service.get_release_status_by_id(release_id)

                        await log(
                            log_type=LogType.INFO,
                            log_message=(
                                f"Пользователю {user_name} предложено место №{spot_id}\n"
                                f"release_status = {release_status}\n"
                                f"request_status = {request_status}"
                            )
                        )
                        waiting_count += 1
                    else:
                        release_owner = spot_release_service.get_release_owner(release_id)

                        if release_owner:
                            release_user_id, release_tg_id = release_owner
                            release_notifications.append({
                                'tg_id': release_tg_id,
                                'spot_number': spot_id,
                                'date': distribution_date
                            })

                        spot_release_service.update_parking_releases(
                            user_id=user_id,
                            release_id=release_id,
                            current_status=ParkingReleaseStatus.ACCEPTED
                        )
                        spot_request_service.update_parking_request_status(
                            request_id=request_id,
                            current_status=ParkingRequestStatus.ACCEPTED
                        )
                        user_service.update_user_rating_by_user_id(
                            db_user_id=user_id,
                            delta=1,
                            user_name=user_name
                        )

                        message_text = await to_user_about_assigned_spot(tg_id, spot_id, distribution_date)
                        await notify_user(tg_id, message_text)

                        request_status = spot_request_service.get_request_status_by_id(request_id)
                        release_status = spot_release_service.get_release_status_by_id(release_id)

                        await log(
                            log_type=LogType.INFO,
                            log_message=(
                                f"Пользователю {user_name} отдано место №{spot_id}\n"
                                f"release_status = {release_status}\n"
                                f"request_status = {request_status}"
                            )
                        )
                        distributed_count += 1

            conn.commit()

            for notification in release_notifications:
                message_text = await to_owner_message(
                    notification['tg_id'],
                    notification['spot_number'],
                    notification['date']
                )
                await notify_user(notification['tg_id'], message_text)

            await update_daily_statistics_by_date(datetime_now)

            await log(
                log_type=LogType.DEBUG,
                log_message=f"Распределение мест окончено\n"
                            f"Распределено {distributed_count} мест(-о)\n"
                            f"Ожидает подтверждения {waiting_count} мест(-о)",
                is_sending_log=False
            )
            return distributed_count
    except Exception as e:
        await log(
            log_message=f"Ошибка при перераспределении парковочных мест: {e}"
        )
