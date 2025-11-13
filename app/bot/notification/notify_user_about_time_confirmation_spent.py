import logging

from app.bot import bot
from app.bot.dto.spot_confirmation_dto import SpotConfirmationDTO
from app.bot.keyboard_markup import return_markup
from app.bot.users.get_user_full_mention import get_user_full_mention


async def notify_user_about_time_confirmation_spent(spot_confirmation_data: SpotConfirmationDTO):
    """Отправляет уведомление пользователю о том что время на занятие места истекло"""
    user = await get_user_full_mention(spot_confirmation_data.tg_user_id)
    try:
        message_text = (
            f"Приветствую, {user}!\n\n"
            f"⏰ Время на подтверждение места истекло!\n\n"
            f"<b>Место:</b> #{spot_confirmation_data.spot_number} на "
            f"{spot_confirmation_data.assignment_date.strftime('%d.%m.%Y')} "
            f"было освобождено для других пользователей.\n\n"
            f"️️⚠️ Я больше не буду предлагать вам места на эту дату"
        )

        await bot.send_message(
            chat_id=spot_confirmation_data.tg_user_id,
            text=message_text,
            reply_markup=return_markup
        )
        return True
    except Exception as e:
        logging.error(f"Error sending notification to user {spot_confirmation_data.tg_user_id}: {e}")
        return False