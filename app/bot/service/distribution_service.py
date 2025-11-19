import logging
import random
from datetime import datetime

import psycopg2

from app.bot.constants.log_types import LogNotification
from app.bot.dto.spot_confirmation_dto import SpotConfirmationDTO
from app.bot.notification.log_notification import send_log_notification
from app.bot.notification.messages.to_owner_message import to_owner_message
from app.bot.notification.messages.to_user_about_assigned_spot import to_user_about_assigned_spot
from app.bot.notification.messages.to_user_about_found_spot import to_user_about_found_spot
from app.bot.notification.notify_user import notify_user
from app.data.init_db import get_db_connection
from app.data.models.releases.parking_releases import ParkingReleaseStatus
from app.data.models.requests.parking_requests import ParkingRequestStatus
from app.data.repository.distribute_parking_spots_repository import update_parking_releases, \
    update_parking_request_status, \
    update_user_rating, get_release_owner, get_candidates, get_dates_with_availability, get_free_spots
from app.data.repository.spot_confirmations_repository import insert_row_of_spot_confirmation
from app.log_text import PARKING_DISTRIBUTION_ERROR, DATABASE_ERROR


async def distribute_parking_spots():
    """
        Распределяет свободные парковочные места среди пользователей в очереди.

        Автоматически назначает доступные места пользователям с наименьшим рейтингом,
        уведомляя обе стороны о результате распределения.

        Возвращает:
            int: количество успешно распределенных мест
        """
    today_date = datetime.today().date()
    today_9am = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    datetime_now = datetime.now()
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                dates_with_availability = await get_dates_with_availability(cur)

                distributed_count = 0
                release_notifications = []

                for distribution_date in dates_with_availability:
                    free_spots = await get_free_spots(cur, distribution_date)

                    if not free_spots:
                        continue

                    candidates = await get_candidates(cur, distribution_date, free_spots)
                    if not candidates:
                        continue

                    min_rating = candidates[0][2]
                    min_rating_candidates = [c for c in candidates if c[2] == min_rating]
                    random.shuffle(min_rating_candidates)
                    selected_candidates = min_rating_candidates[:len(free_spots)]

                    for i, (request_id, user_id, current_rating, tg_id) in enumerate(selected_candidates):
                        release_id, spot_id = free_spots[i]

                        if (distribution_date == today_date) and (datetime_now > today_9am):

                            await update_parking_releases(cur, user_id, release_id, ParkingReleaseStatus.WAITING)
                            await update_parking_request_status(cur, request_id,
                                                                ParkingRequestStatus.WAITING_CONFIRMATION)

                            spot_confirmation_data = SpotConfirmationDTO(
                                str(user_id), tg_id, spot_id, distribution_date, release_id, request_id
                            )
                            await insert_row_of_spot_confirmation(cur, user_id, release_id, request_id)

                            message_text = await to_user_about_found_spot(spot_confirmation_data)
                            await notify_user(tg_id, message_text, True)

                        else:
                            release_owner = await get_release_owner(cur, release_id)

                            if release_owner:
                                release_user_id, release_tg_id = release_owner
                                release_notifications.append({
                                    'tg_id': release_tg_id,
                                    'spot_number': spot_id,
                                    'date': distribution_date
                                })

                            await update_parking_releases(cur, user_id, release_id, ParkingReleaseStatus.ACCEPTED)

                            await update_parking_request_status(cur, request_id, ParkingRequestStatus.ACCEPTED)

                            await update_user_rating(cur, user_id)

                            message_text = await to_user_about_assigned_spot(tg_id, spot_id, distribution_date)
                            await notify_user(tg_id, message_text)
                            distributed_count += 1

                conn.commit()
                for notification in release_notifications:
                    message_text = await to_owner_message(
                        notification['tg_id'],
                        notification['spot_number'],
                        notification['date']
                    )
                    await notify_user(notification['tg_id'], message_text)
                logging.debug(f"Distributed {distributed_count} parking spots")
                return distributed_count

    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))
    except Exception as e:
        logging.error(PARKING_DISTRIBUTION_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, PARKING_DISTRIBUTION_ERROR.format(e))
        return 0
