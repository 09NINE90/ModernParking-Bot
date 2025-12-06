from app.logs.log_builder import log


async def delete_message(chat_id: int, message_id: int):
    try:
        from app.bot import bot
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
    except Exception as e:
        await log(
            log_message=f"Ошибка удаления сообщения: {e}"
        )