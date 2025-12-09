import logging

from aiogram.enums import ParseMode

from app.config import settings


async def send_log(topic_id: int = 1, log_message: str = "", parse_mode: ParseMode = ParseMode.MARKDOWN):
    try:
        from app.bot import bot
        await bot.send_message(
            chat_id=settings.TECH_GROUP_ID,
            message_thread_id=topic_id,
            text=log_message,
            parse_mode=parse_mode
        )
    except Exception as e:
        logging.error(f"Error sending logs: {e}")
