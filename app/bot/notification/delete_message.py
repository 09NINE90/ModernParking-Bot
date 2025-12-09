import logging


async def delete_message(chat_id: int, message_id: int):
    try:
        from app.bot.config import bot
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
    except Exception as e:
        logging.error(f"Error while deleting message: {e}")