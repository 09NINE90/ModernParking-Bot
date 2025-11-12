import logging

from app.bot import bot
from app.bot.keyboard_markup import return_markup


async def statistics_notification(tg_chat_id: int, message: str, assignment_date):
    """Отправляет уведомление пользователю о назначении места"""
    try:
        message_text = (
            f"👋<b>Всем привет!</b>\n"
            f"<u>Сегодня: {assignment_date.strftime('%d.%m.%Y')}:</u>\n"
            f"{message}"
        )

        try:
            await bot.get_chat(tg_chat_id)
        except Exception as e:
            logging.error(f"Нет доступа к чату {tg_chat_id}: {e}")
            return False

        await bot.send_message(
            chat_id=tg_chat_id,
            text=message_text,
            reply_markup=return_markup
        )
        return True
    except Exception as e:
        logging.error(f"Error sending notification to user {tg_chat_id}: {e}")
        return False