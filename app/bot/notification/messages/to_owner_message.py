from app.bot.utils import get_user_full_mention
from app.utils.emoji_util import sber_emoji, date_emoji, spot_emoji, sber_accept_emoji, sber_spot_emoji, sber_date_emoji


async def to_owner_message(tg_user_id: int, spot_number: int, assignment_date):
    user = await get_user_full_mention(tg_user_id)

    message_text = (
        f"Приветствую, {user}\n\n"
        f"{sber_accept_emoji} Ваше парковочное место назначено!\n\n"
        f"{sber_spot_emoji} <b>Место:</b> №{spot_number}\n"
        f"{sber_date_emoji} <b>Дата:</b> {assignment_date.strftime('%d.%m.%Y')}"
    )
    return message_text