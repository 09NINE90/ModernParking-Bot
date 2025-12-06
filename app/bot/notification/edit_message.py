from app.logs.log_builder import log


async def edit_message(tg_chat_id, editing_message_id, new_message_text):
    try:
        from app.bot import bot
        await bot.edit_message_text(
            chat_id=tg_chat_id,
            message_id=editing_message_id,
            text=new_message_text
        )
    except Exception as e:
        await log(
            log_message=f"Ошибка редактирования сообщения: {e}"
        )
