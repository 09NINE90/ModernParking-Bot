from datetime import datetime, timedelta

from app.bot.config import GROUP_ID, CHANNEL_ID
from app.bot.constants.car_emojis import get_random_car_emoji
from app.bot.notification.daily_statistics_notification import daily_statistics_notification
from app.bot.notification.weeky_statistics_notification import weekly_statistics_notification
from app.bot.users.get_user_full_mention import get_user_full_mention
from app.data.init_db import get_db_connection
from app.data.models.parking_releases import ParkingReleaseStatus
from app.data.models.parking_requests import ParkingRequestStatus
from app.data.models.parking_transfers import ParkingTransfer
from app.data.repository.parking_releases_repository import free_parking_releases_by_date, \
    parking_releases_by_week
from app.data.repository.parking_requests_repository import parking_requests_by_week
from app.data.repository.statistics_repository import get_parking_transfers_by_date, get_parking_transfers_by_week


async def daily_statistics_service(plus_day=0):
    day = datetime.today() + timedelta(days=plus_day)
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


async def weekly_statistics_service():
    today = datetime.now()
    monday_date = today - timedelta(days=today.weekday())
    friday_date = monday_date + timedelta(days=4)
    with (get_db_connection() as conn):
        with conn.cursor() as cur:
            accepted_parking_releases = await parking_releases_by_week(cur, ParkingReleaseStatus.ACCEPTED.value,
                                                                       monday_date.date(), friday_date.date())
            accepted_spots_count = len(accepted_parking_releases)

            not_found_parking_requests = await parking_requests_by_week(cur, ParkingRequestStatus.NOT_FOUND.value,
                                                                        monday_date.date(), friday_date.date())
            not_found_spots_count = len(not_found_parking_requests)

            canceled_parking_requests = await parking_requests_by_week(cur, ParkingRequestStatus.CANCELED.value,
                                                                        monday_date.date(), friday_date.date())
            canceled_spots_count = len(canceled_parking_requests)

            results = await get_parking_transfers_by_week(cur, monday_date.date(), friday_date.date())
            transfers = [ParkingTransfer(spot_id=row[0], recipient_tg_id=row[1], owner_tg_id=row[2])
                         for row in results]

            message_text = (f"\n✅ Реализовано мест всего: {accepted_spots_count}\n"
                            f"🤷‍♂️ Не найдено мест по запросу: {not_found_spots_count}\n"
                            f"❌ Отклонено мест: {canceled_spots_count}\n")
            if len(transfers) > 0:
                message_text += "\nТрансферы мест:\n"
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
