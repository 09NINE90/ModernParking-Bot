import logging

from app.bot.config import bot


async def remind_user_of_spot(user_tg_id, spot_id):
    """Отправляет уведомление пользователю о том, что на завтра у него есть место"""
    try:
        message_text = (
            f"🔔 <b>Напоминание</b>\n"
            f"На завтра Вам забронировано место <b>№{spot_id}</b>"
        )

        try:
            await bot.get_chat(user_tg_id)
        except Exception as e:
            logging.error(f"Нет доступа к чату {user_tg_id}: {e}")
            return False

        await bot.send_message(
            chat_id=user_tg_id,
            text=message_text
        )
        return True
    except Exception as e:
        logging.error(f"Error sending reminder to user {user_tg_id}: {e}")
        return False