from app.bot.utils import get_user_full_mention


async def to_user_about_assigned_spot(tg_user_id: int, spot_number: int, assignment_date):
    user = await get_user_full_mention(tg_user_id)

    message_text = (
        f"Приветствую, {user}\n\n"
        f"🎉 Вам назначено парковочное место!\n\n"
        f"📍 <b>Место:</b> №{spot_number}\n"
        f"📅 <b>Дата:</b> {assignment_date.strftime('%d.%m.%Y')}\n\n"
        f"Поздравляем с получением места!"
    )

    return message_text