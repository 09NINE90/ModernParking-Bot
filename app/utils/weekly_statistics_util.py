from datetime import datetime, timedelta, date

from aiogram.enums import ParseMode

from app.bot.notification.send_log import send_log
from app.bot.notification.statistics import send_and_pin_message_in_chat
from app.bot.utils import get_user_full_mention
from app.config import settings
from app.data import get_db_connection
from app.services import ServiceFactory
from app.utils.emoji_util import get_random_car_emoji, statistics_emoji, eyes_emoji, sber_arrow_emoji, \
    sber_accept_emoji, canceled_emoji, not_found_emoji


async def get_weekly_statistics():
    today = datetime.now()
    monday_date = today - timedelta(days=today.weekday())
    friday_date = monday_date + timedelta(days=4)

    start_date = monday_date.date()
    end_date = friday_date.date()

    with get_db_connection() as conn:
        statistics_service = ServiceFactory.create_statistics_service(conn)

        statistics_data = statistics_service.get_statistics_by_date_range(
            start_date=start_date,
            end_date=end_date
        )

        transfers = statistics_service.get_parking_transfers_by_date_range(
            start_date=start_date,
            end_date=end_date
        )

        message_text = get_start_message_text(start_date, friday_date, statistics_data)

        if len(transfers) > 0:
            message_text += "\n<b>Трансферы мест:</b>\n"
            for transfer in transfers:
                emoji = get_random_car_emoji()
                recipient = await get_user_full_mention(user_id=transfer.recipient_tg_id, is_link=True)
                owner = await get_user_full_mention(user_id=transfer.owner_tg_id, is_link=True)
                spot = transfer.spot_id
                message_text += f"{emoji} {owner} отдал место <b>№{spot}</b> -> {recipient}\n\n"
        else:
            message_text += f"{eyes_emoji}Трансферов мест пока не было..."

        await send_and_pin_message_in_chat(
            tg_chat_id=settings.GROUP_ID,
            message_text=message_text,
            is_pinned=True
        )

        await send_log(
            topic_id=settings.STATS_TOPIC_ID,
            log_message=message_text,
            parse_mode=ParseMode.HTML
        )

        return None


def get_start_message_text(start_date: date, end_date: date, statistics_data):
    message_text = (
        f"<b>Всем привет!</b>\n"
        f"{statistics_emoji} <b>Статистика за текущую неделю</b> "
        f"<u>{start_date.strftime('%d.%m.%Y')}-{end_date.strftime('%d.%m.%Y')}</u>:\n\n"
        f"{sber_arrow_emoji} Всего освобождено мест: <b>{statistics_data['total_releases']}</b>\n"
        f"{sber_arrow_emoji} Всего запросов на места: <b>{statistics_data['total_requests']}</b>\n\n"
        f"{sber_accept_emoji} Реализовано мест всего: <b>{statistics_data['accepted_releases_count']}</b>\n"
        f"{not_found_emoji}️ Не найдено мест по запросу: <b>{statistics_data['not_found_requests_count']}</b>\n"
        f"{canceled_emoji} Отозвано запросов на места: <b>{statistics_data['canceled_requests_count']}</b>\n"
    )

    return message_text
