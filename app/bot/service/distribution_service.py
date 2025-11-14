import logging
import random
from datetime import datetime

from app.bot.dto.spot_confirmation_dto import SpotConfirmationDTO
from app.bot.notification.notify_owner_about_taken_spot import notify_owner_about_taken_spot
from app.bot.notification.notify_user_about_assigned_spot import notify_user_about_assigned_spot
from app.bot.notification.notify_user_about_found_spot import notify_user_about_found_spot
from app.data.init_db import get_db_connection
from app.data.models.parking_releases import ParkingReleaseStatus
from app.data.models.parking_requests import ParkingRequestStatus
from app.data.repository.distribute_parking_spots_repository import update_parking_releases, \
    update_parking_request_status, \
    update_user_rating, get_release_owner, get_candidates, get_dates_with_availability, get_free_spots


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
                            await notify_user_about_found_spot(spot_confirmation_data)

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

                            await notify_user_about_assigned_spot(tg_id, spot_id, distribution_date)
                            distributed_count += 1

                conn.commit()
                for notification in release_notifications:
                    await notify_owner_about_taken_spot(
                        notification['tg_id'],
                        notification['spot_number'],
                        notification['date']
                    )
                logging.debug(f"Distributed {distributed_count} parking spots")
                return distributed_count

    except Exception as e:
        logging.error(f"Error distributing parking spots: {e}")
        return 0
