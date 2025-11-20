from app.data.models.spot_confirmation_dto import SpotConfirmationDTO
from app.bot.users.get_user_full_mention import get_user_full_mention


async def to_user_about_time_confirmation_spent(spot_confirmation_data: SpotConfirmationDTO):
    user = await get_user_full_mention(spot_confirmation_data.tg_user_id)

    message_text = (
        f"Приветствую, {user}!\n\n"
        f"⏰ Время на подтверждение места истекло!\n\n"
        f"<b>Место:</b> №{spot_confirmation_data.spot_number} на "
        f"{spot_confirmation_data.assignment_date.strftime('%d.%m.%Y')} "
        f"было освобождено для других пользователей.\n\n"
        f"️️⚠️ Я больше не буду предлагать вам места на эту дату"
    )

    return message_text