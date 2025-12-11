from aiogram.exceptions import TelegramBadRequest

from app.logs.log_builder import log, LogType


async def edit_message(tg_chat_id, editing_message_id, new_message_text):
    try:
        from app.bot import bot
        await bot.edit_message_text(
            chat_id=tg_chat_id,
            message_id=editing_message_id,
            text=new_message_text
        )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await log(
                log_type=LogType.WARN,
                log_message=f"Новый текст сообщения похож на старый: {e}"
            )
            return
        await log(
            log_message=f"TelegramBadRequest при редактировании сообщения: {e}",
        )
    except Exception as e:
        await log(
            log_message=f"Ошибка редактирования сообщения: {e}"
        )
