import logging
from datetime import datetime

from aiogram.enums import ParseMode

from app.bot.config import CHANNEL_ID, bot
from app.bot.constants.emoji_status import get_log_emoji
from app.bot.constants.log_types import LogNotification


async def send_log_notification(log_type: LogNotification, message):
    try:
        log_emoji = await get_log_emoji(log_type)
        datetime_now = datetime.now()
        message_text = (
            f"{datetime_now.strftime('%d.%m.%Y %H:%M:%S')}\n"
            f"{log_emoji} type - {log_type.name}\n"
            f"```"
            f"{message}"
            f"```"
        )

        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=message_text,
            parse_mode=ParseMode.MARKDOWN
        )
        return True
    except Exception as e:
        logging.error(f"Error sending logs: {e}")
        return False
