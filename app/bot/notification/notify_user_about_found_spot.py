import logging


from app.bot import bot
from aiogram.fsm.context import FSMContext
from app.bot.dto.spot_confirmation_dto import SpotConfirmationDTO
from app.bot.keyboard_markup import found_spot_markup
from app.bot.schedule.scheduler_manager import schedule_spot_cancellation
from app.bot.users.get_user_full_mention import get_user_full_mention


async def notify_user_about_found_spot(spot_confirmation_data: SpotConfirmationDTO, state: FSMContext):
    """Отправляет уведомление пользователю о найденном месте по его запросу"""
    user = await get_user_full_mention(spot_confirmation_data.tg_user_id)
    delay = 5
    try:
        await state.update_data(confirmation_data=spot_confirmation_data)

        cancel_time = await schedule_spot_cancellation(state, spot_confirmation_data, delay_minutes=delay)

        message_text = (
            f"Приветствую, {user}!\n\n"
            f"🎯 По вашему запросу найдено свободное парковочное место!\n\n"
            f"📍 <b>Место:</b> #{spot_confirmation_data.spot_number}\n"
            f"📅 <b>Дата:</b> {spot_confirmation_data.assignment_date.strftime('%d.%m.%Y')}\n\n"
            f"⚠️ <b>У вас {delay} минут на подтверждение!</b>\n"
            f"⏰ До: {cancel_time.strftime('%H:%M')}\n\n"
            f"• Подтвердите, что займете это место\n"
            f"• Или отклоните, если оно вам не нужно\n\n"
            f"После истечения времени место будет автоматически освобождено"
        )

        await bot.send_message(
            chat_id=spot_confirmation_data.tg_user_id,
            text=message_text,
            reply_markup=found_spot_markup
        )
        return True
    except Exception as e:
        logging.error(f"Error sending notification to user {spot_confirmation_data.tg_user_id}: {e}")
        return False
