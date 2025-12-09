from app.bot.utils import get_user_full_mention


async def to_owner_message(tg_user_id: int, spot_number: int, assignment_date):
    user = await get_user_full_mention(tg_user_id)

    message_text = (
        f"Приветствую, {user}\n\n"
        f"✅ Ваше парковочное место назначено!\n\n"
        f"📍 <b>Место:</b> №{spot_number}\n"
        f"📅 <b>Дата:</b> {assignment_date.strftime('%d.%m.%Y')}"
    )
    return message_text