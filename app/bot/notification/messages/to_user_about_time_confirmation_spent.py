from app.bot.utils import get_user_full_mention
from app.data.models import SpotConfirmationDTO


async def to_user_about_time_confirmation_spent(spot_confirmation_data: SpotConfirmationDTO):
    user = await get_user_full_mention(spot_confirmation_data.tg_user_id)

    message_text = (
        f"Приветствую, {user}!\n\n"
        f"⏰ Время на подтверждение места истекло!\n\n"
        f"<b>Место:</b> №{spot_confirmation_data.spot_number} на "
        f"{spot_confirmation_data.assignment_date.strftime('%d.%m.%Y')} "
        f"было освобождено для других пользователей.\n\n"
        f"️️ℹ️️ <i>Если освободится еще одно место на сегодня, я Вам его предложу</i>"
    )

    return message_text