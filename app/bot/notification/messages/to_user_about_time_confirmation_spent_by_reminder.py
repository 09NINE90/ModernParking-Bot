from app.bot.utils import get_user_full_mention
from app.data.models import ParkingReminder
from app.utils.emoji_util import warn_emoji, clock_emoji


async def to_user_about_time_confirmation_spent_by_reminder(reminder_data: ParkingReminder):
    user = await get_user_full_mention(reminder_data.user_tg_id)

    message_text = (
        f"Приветствую, {user}!\n\n"
        f"{clock_emoji} Время на подтверждение места истекло!\n\n"
        f"<b>Место:</b> №{reminder_data.spot_id} на "
        f"{reminder_data.release_date.strftime('%d.%m.%Y')} "
        f"было освобождено для других пользователей.\n\n"
        f"️{warn_emoji} <i>Вы не успели подтвердить занятие места</i>"
    )

    return message_text