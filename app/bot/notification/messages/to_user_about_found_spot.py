from app.bot.utils import get_user_full_mention
from app.config import settings
from app.data.models.dto.spot_confirmation_dto import SpotConfirmationDTO


async def to_user_about_found_spot(spot_confirmation_data: SpotConfirmationDTO):
    user = await get_user_full_mention(spot_confirmation_data.tg_user_id)
    delay_minutes = settings.DELAY_MINUTES_CONFIRM_SPOT

    from app.scheduler.scheduler_manager import schedule_spot_cancellation
    cancel_time = await schedule_spot_cancellation(spot_confirmation_data, delay_minutes=delay_minutes)

    message_text = (
        f"Приветствую, {user}!\n\n"
        f"🎯 По вашему запросу найдено свободное парковочное место!\n\n"
        f"📍 <b>Место:</b> №{spot_confirmation_data.spot_number}\n"
        f"📅 <b>Дата:</b> {spot_confirmation_data.assignment_date.strftime('%d.%m.%Y')}\n\n"
        f"⚠️ <b>У Вас {delay_minutes} минута на подтверждение!</b>\n"
        f"⏰ До: {cancel_time.strftime('%H:%M')}\n\n"
        f"• Подтвердите, что займете это место\n"
        f"• Или отклоните, если оно вам не нужно\n\n"
        f"После истечения времени место будет автоматически освобождено"
    )

    return message_text
