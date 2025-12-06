from app.bot.notification.utils.unpin_pin_message_util import unpin_last_message, pin_last_message
from app.bot.notification.utils.chat_access_util import chat_access_required
from app.logs.log_builder import log


@chat_access_required
async def send_and_pin_message_in_chat(tg_chat_id: int, message_text: str, is_pinned: bool = False):
    try:
        from app.bot import bot
        sent_message = await bot.send_message(
            chat_id=tg_chat_id,
            text=message_text
        )

        if is_pinned:
            await unpin_last_message(tg_chat_id)
            await pin_last_message(tg_chat_id, sent_message)

        return True
    except Exception as e:
        await log(
            log_message=f"Ошибка отправки сообщения в чат {tg_chat_id}: {e}"
        )
        return False
