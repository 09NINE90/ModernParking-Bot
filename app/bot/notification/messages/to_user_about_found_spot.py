from app.bot.config import DELAY_MINUTES_CONFIRM_SPOT
from app.data.models.spot_confirmation.spot_confirmation_dto import SpotConfirmationDTO
from app.bot.users.get_user_full_mention import get_user_full_mention
from app.schedule.scheduler_manager import schedule_spot_cancellation


async def to_user_about_found_spot(spot_confirmation_data: SpotConfirmationDTO):
    user = await get_user_full_mention(spot_confirmation_data.tg_user_id)
    delay_minutes = DELAY_MINUTES_CONFIRM_SPOT

    cancel_time = await schedule_spot_cancellation(spot_confirmation_data, delay_minutes=delay_minutes)

    message_text = (
        f"Приветствую, {user}!\n\n"
        f"🎯 По вашему запросу найдено свободное парковочное место!\n\n"
        f"📍 <b>Место:</b> №{spot_confirmation_data.spot_number}\n"
        f"📅 <b>Дата:</b> {spot_confirmation_data.assignment_date.strftime('%d.%m.%Y')}\n\n"
        f"⚠️ <b>У вас {delay_minutes} минут на подтверждение!</b>\n"
        f"⏰ До: {cancel_time.strftime('%H:%M')}\n\n"
        f"• Подтвердите, что займете это место\n"
        f"• Или отклоните, если оно вам не нужно\n\n"
        f"После истечения времени место будет автоматически освобождено"
    )

    return message_text