import logging

from app.bot import bot
from app.bot.keyboard_markup import return_markup
from app.bot.users.get_user_full_mention import get_user_full_mention


async def notify_user_about_assigned_spot(tg_user_id: int, spot_number: int, assignment_date):
    """Отправляет уведомление пользователю о назначении места"""
    user = await get_user_full_mention(tg_user_id)
    try:
        message_text = (
            f"Приветствую, {user}\n\n"
            f"🎉 Вам назначено парковочное место!\n\n"
            f"📍 <b>Место:</b> #{spot_number}\n"
            f"📅 <b>Дата:</b> {assignment_date.strftime('%d.%m.%Y')}\n\n"
            f"Поздравляем с получением места!"
        )

        await bot.send_message(
            chat_id=tg_user_id,
            text=message_text,
            reply_markup=return_markup
        )
        return True
    except Exception as e:
        logging.error(f"Error sending notification to user {tg_user_id}: {e}")
        return False