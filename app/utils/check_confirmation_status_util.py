from app.bot.notification.edit_message import edit_message
from app.data import get_db_connection
from app.services import ServiceFactory


async def expire_waiting_confirmations():
    """
        Ежедневно в 18:00:
        - находит все WAITING-подтверждения;
        - переводит их в CANCELLED;
        - запросы -> CANCELED;
        - релизы PENDING/WAITING -> NOT_FOUND;
        - редактирует сообщения пользователей.
    """
    with get_db_connection() as conn:
        spot_release_service = ServiceFactory.create_spot_release_service(conn)
        spot_request_service = ServiceFactory.create_spot_request_service(conn)
        spot_confirmation_service = ServiceFactory.create_spot_confirmation_service(conn)

        confirmations = spot_confirmation_service.get_all_waiting_confirmations_with_user()

        spot_confirmation_service.bulk_cancel_all_waiting()
        spot_request_service.bulk_cancel_requests_by_confirmations(confirmations)
        spot_release_service.mark_releases_not_found_if_only_cancelled(confirmations)

        conn.commit()

    for conf in confirmations:
        conf_id, user_id, request_id, release_id, message_id, tg_id = conf
        await edit_message(
            tg_chat_id=tg_id,
            editing_message_id=message_id,
            new_message_text="Вам было предложено место на сегодня."
                             " Но время на принятие места вышло😔\n\n"
                             "<i>ℹ️ Ваша заявка отменена.</i>"
        )
