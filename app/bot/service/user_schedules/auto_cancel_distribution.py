import logging

from app.bot.config import bot
from app.bot.keyboard_markup import return_markup


async def auto_cancel_distribution(tg_id, message_id):
    try:
        new_text = "⏳ <b>Время для выбора расписания истекло.</b>"

        await bot.edit_message_text(
            chat_id=tg_id,
            message_id=message_id,
            text=new_text,
            reply_markup=return_markup
        )

        logging.info(f"Message {message_id} for {tg_id} was auto-edited due to timeout")

    except Exception as e:
        logging.error(f"Failed to auto-edit message for {tg_id}: {e}")