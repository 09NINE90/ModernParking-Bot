from datetime import datetime, timedelta

from app.bot.utils import get_user_full_mention
from app.utils.emoji_util import warn_emoji, congratulation_emoji, date_emoji, spot_emoji, sber_date_emoji, \
    sber_spot_emoji


async def to_user_about_assigned_spot(tg_user_id: int, spot_number: int, assignment_date):
    user = await get_user_full_mention(tg_user_id)

    datetime_now = datetime.now()
    today_18_00 = datetime_now.replace(hour=18, minute=0, second=0, microsecond=0)
    tomorrow = datetime_now.date() + timedelta(days=1)

    if (assignment_date == tomorrow) and (datetime_now >= today_18_00):
        info_text = ""
    else:
        info_text = ("\n\n"
                     f"{warn_emoji} <i>Не забудте подвердить место накануне назначенной даты с 18:00 до 00:00</i>")


    message_text = (
        f"Приветствую, {user}\n\n"
        f"{congratulation_emoji} Вам назначено парковочное место!\n\n"
        f"{sber_spot_emoji} <b>Место:</b> №{spot_number}\n"
        f"{sber_date_emoji} <b>Дата:</b> {assignment_date.strftime('%d.%m.%Y')}\n\n"
        f"Поздравляем с получением места!"
        f"{info_text}"
    )

    return message_text