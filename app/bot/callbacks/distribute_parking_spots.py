import logging
import random

from app.data.init_db import get_db_connection
from app.bot.notification.send_spot_assignment_notification import send_spot_request_assignment_notification, \
    send_spot_release_assignment_notification
from app.data.repository.distribute_parking_spots_repository import update_parking_releases, update_parking_request_status, \
    update_user_rating, get_release_owner, get_candidates, get_dates_with_availability, get_free_spots

async def distribute_parking_spots():
    """
        Распределяет свободные парковочные места среди пользователей в очереди.

        Автоматически назначает доступные места пользователям с наименьшим рейтингом,
        уведомляя обе стороны о результате распределения.

        Возвращает:
            int: количество успешно распределенных мест
        """
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

                        release_owner = await get_release_owner(cur, release_id)

                        if release_owner:
                            release_user_id, release_tg_id = release_owner
                            release_notifications.append({
                                'tg_id': release_tg_id,
                                'spot_number': spot_id,
                                'date': distribution_date
                            })

                        await update_parking_releases(cur, user_id, release_id)

                        await update_parking_request_status(cur, request_id)

                        await update_user_rating(cur, user_id)

                        await send_spot_request_assignment_notification(tg_id, spot_id, distribution_date)
                        distributed_count += 1

                conn.commit()
                for notification in release_notifications:
                    await send_spot_release_assignment_notification(
                        notification['tg_id'],
                        notification['spot_number'],
                        notification['date']
                    )
                logging.info(f"Distributed {distributed_count} parking spots")
                return distributed_count

    except Exception as e:
        logging.error(f"Error distributing parking spots: {e}")
        return 0
