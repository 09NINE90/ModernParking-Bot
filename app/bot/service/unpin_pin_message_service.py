import logging

from app.bot.config import bot
from app.bot.constants.log_types import LogNotification
from app.bot.notification.log_notification import send_log_notification
from app.log_text import UNPINNED_MESSAGE_PROCESSING_WARNING, PINNED_MESSAGE_PROCESSING_WARNING


async def unpin_last_message(tg_chat_id):
    try:
        pinned_message = await bot.get_chat(tg_chat_id)
        if pinned_message.pinned_message:
            if pinned_message.pinned_message.from_user.id == (await bot.get_me()).id:
                await bot.unpin_chat_message(
                    chat_id=tg_chat_id,
                    message_id=pinned_message.pinned_message.message_id
                )
    except Exception as e:
        logging.warning(UNPINNED_MESSAGE_PROCESSING_WARNING.format(e))
        await send_log_notification(LogNotification.WARN, UNPINNED_MESSAGE_PROCESSING_WARNING.format(e))

async def pin_last_message(tg_chat_id, sent_message):
    try:
        await bot.pin_chat_message(
            chat_id=tg_chat_id,
            message_id=sent_message.message_id,
            disable_notification=True
        )
    except Exception as e:
        logging.warning(PINNED_MESSAGE_PROCESSING_WARNING.format(e))
        await send_log_notification(LogNotification.WARN, PINNED_MESSAGE_PROCESSING_WARNING.format(e))