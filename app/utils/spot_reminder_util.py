from datetime import date, timedelta

from app.bot.notification.enumz import NotificationTypes
from app.bot.notification.messages import to_remind_user_of_spot
from app.bot.notification.notify_user import notify_user
from app.data import get_db_connection
from app.services import ServiceFactory


async def spot_reminder():
    """
        Асинхронная функция для отправки напоминаний пользователям о парковочных местах на завтра.
    """
    tomorrow = date.today() + timedelta(days=1)

    with get_db_connection() as conn:
        spot_release_service = ServiceFactory.create_spot_release_service(conn)
        reminder_service = ServiceFactory.create_reminder_spot_service(conn)

        current_spots_releases = spot_release_service.get_accepted_spot_by_date(tomorrow)

        if len(current_spots_releases) > 0:
            for release in current_spots_releases:
                reminder_id = reminder_service.create_reminder_spot_confirmations(
                    user_id=release.db_user_id,
                    release_id=release.release_id,
                    request_id=release.request_id
                )

                message_text = await to_remind_user_of_spot(release)
                sent_message_id = await notify_user(
                    tg_user_id=release.user_tg_id,
                    message_text=message_text,
                    notification_type=NotificationTypes.SPOT_REMINDER
                )

                reminder_service.set_message_sent_id(
                    reminder_id=reminder_id,
                    message_sent_id=sent_message_id
                )

                conn.commit()
