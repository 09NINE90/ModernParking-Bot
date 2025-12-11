from app.bot.utils import get_user_full_mention
from app.data.models.dto.spot_confirmation_dto import SpotConfirmationDTO


async def to_user_about_found_spot(spot_confirmation_data: SpotConfirmationDTO):
    user = await get_user_full_mention(spot_confirmation_data.tg_user_id)

    message_text = (
        f"Приветствую, {user}!\n\n"
        f"🎯 По вашему запросу найдено свободное парковочное место на <b>сегодня</b>!\n\n"
        f"📍 <b>Место:</b> №{spot_confirmation_data.spot_number}\n"
        f"📅 <b>Дата:</b> {spot_confirmation_data.assignment_date.strftime('%d.%m.%Y')}\n\n"
        f"• Подтвердите, что займете это место\n"
        f"• Или отклоните, если оно вам не нужно\n\n"
        f"⚠️ <i>Кто первый успеет принять место, тому оно будет назначено!</i>"
    )

    return message_text
