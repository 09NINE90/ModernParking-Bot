from app.bot.constants.car_emojis import get_random_car_emoji
from app.bot.constants.group_id import GROUP_ID
from app.bot.notification.statistics_notification import statistics_notification
from app.bot.users.get_user_full_mention import get_user_full_mention
from app.data.init_db import get_db_connection
from app.data.models.parking_transfers import ParkingTransfer
from app.data.repository.parking_releases_repository import free_parking_releases_by_date
from app.data.repository.statistics_repository import get_parking_transfers_by_date


async def statistics_service(day):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            free_parking_releases = await free_parking_releases_by_date(cur, day.date())
            free_spots = len(free_parking_releases)

            results = await get_parking_transfers_by_date(cur, day.date())
            transfers = [ParkingTransfer(spot_id=row[0], recipient_tg_id=row[1], owner_tg_id=row[2])
                         for row in results]

            message_text = f"\nСвободных мест всего: {free_spots}\n"
            if len(transfers) > 0:
                message_text += "\nТрансферы мест:\n"
                for transfer in transfers:
                    emoji = get_random_car_emoji()
                    recipient = await get_user_full_mention(transfer.recipient_tg_id)
                    owner = await get_user_full_mention(transfer.owner_tg_id)
                    spot = transfer.spot_id
                    message_text += f"{emoji} {owner} отдал место <b>№{spot}</b> -> {recipient}\n\n"

                await statistics_notification(tg_chat_id=GROUP_ID, message=message_text,
                                              assignment_date=day.date())
            else:
                message_text += "👀Трансферов мест пока не было..."
                await statistics_notification(tg_chat_id=GROUP_ID, message=message_text,
                                              assignment_date=day.date())