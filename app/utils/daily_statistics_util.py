from datetime import datetime, timedelta

from aiogram.enums import ParseMode

from app.bot.notification.edit_message import edit_message
from app.bot.notification.send_log import send_log
from app.bot.notification.statistics import send_and_pin_message_in_chat
from app.bot.notification.utils.unpin_pin_message_util import get_last_pinned_message_id
from app.bot.utils import get_user_full_mention
from app.config import settings
from app.data import get_db_connection
from app.logs.log_builder import log, LogType
from app.services import ServiceFactory
from app.utils.dates_util import get_day_text
from app.utils.emoji_util import get_random_car_emoji


async def get_daily_statistics(plus_day: int = 0):
    day = datetime.today() + timedelta(days=plus_day)
    message_text = await get_daily_statistics_text_by_date(day)

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


async def update_daily_statistics_by_date(rq_datetime: datetime):
    if rq_datetime.weekday() >= 5:
        return None

    today_7_30 = rq_datetime.replace(hour=7, minute=30, second=0, microsecond=0)
    today_18_30 = rq_datetime.replace(hour=18, minute=30, second=0, microsecond=0)

    if rq_datetime <= today_7_30:
        return None
    elif rq_datetime >= today_18_30:
        return None

    await log(
        log_type=LogType.DEBUG,
        log_message="Начало изменения текста закрепленного сообщения",
        is_sending_log=False
    )
    editing_message_id = await get_last_pinned_message_id(settings.GROUP_ID)

    if editing_message_id is None:
        return None

    message_text = await get_daily_statistics_text_by_date(rq_datetime)

    await edit_message(
        tg_chat_id=settings.GROUP_ID,
        editing_message_id=editing_message_id,
        new_message_text=message_text,
    )

    await log(
        log_type=LogType.DEBUG,
        log_message="Окончание изменения текста закрепленного сообщения",
        is_sending_log=False
    )
    return None


async def get_daily_statistics_text_by_date(rq_datetime: datetime):
    day_text = get_day_text(rq_datetime.date())

    message_text = (
        f"👋<b>Всем привет!</b>\n"
        f"📊 Ситуация на {day_text} <u>{rq_datetime.date().strftime('%d.%m.%Y')}</u>:\n\n"
    )
    with get_db_connection() as conn:
        spot_release_service = ServiceFactory.create_spot_release_service(conn)
        statistics_service = ServiceFactory.create_statistics_service(conn)

        free_parking_releases = spot_release_service.get_free_parking_releases_by_date(
            rq_date=rq_datetime.date()
        )
        free_spots = len(free_parking_releases)

        transfers = statistics_service.get_parking_transfers_by_date(
            rq_date=rq_datetime.date()
        )

        message_text = (f"{message_text}"
                        f"Свободных мест всего: <b>{free_spots}</b>\n")
        if len(transfers) > 0:
            message_text += "\n<b>Трансферы мест:</b>\n"
            for transfer in transfers:
                emoji = get_random_car_emoji()
                recipient = await get_user_full_mention(user_id=transfer.recipient_tg_id, is_link=True)
                owner = await get_user_full_mention(user_id=transfer.owner_tg_id, is_link=True)
                spot = transfer.spot_id
                message_text += f"{emoji} {owner} отдал место <b>№{spot}</b> -> {recipient}\n\n"
        else:
            message_text += "\n👀Трансферов мест пока не было...\n"

        message_text = (f"{message_text}\n"
                        f"<i>Актуально на {rq_datetime.strftime('%d.%m.%Y %H:%M')}</i>")

        return message_text
