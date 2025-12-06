from app.logs.log_builder import log


async def unpin_last_message(tg_chat_id):
    try:
        from app.bot import bot
        pinned_message = await bot.get_chat(tg_chat_id)
        if pinned_message.pinned_message:
            if pinned_message.pinned_message.from_user.id == (await bot.get_me()).id:
                await bot.unpin_chat_message(
                    chat_id=tg_chat_id,
                    message_id=pinned_message.pinned_message.message_id
                )
    except Exception as e:
        await log(
            log_message=f"Ошибка открепления сообщения в чате {tg_chat_id}: {e}"
        )


async def pin_last_message(tg_chat_id, sent_message):
    try:
        from app.bot import bot
        await bot.pin_chat_message(
            chat_id=tg_chat_id,
            message_id=sent_message.message_id,
            disable_notification=True
        )
    except Exception as e:
        await log(
            log_message=f"Ошибка закрепления сообщения в чате {tg_chat_id}: {e}"
        )


async def get_last_pinned_message_id(tg_chat_id):
    try:
        from app.bot import bot

        chat = await bot.get_chat(tg_chat_id)
        pinned = chat.pinned_message

        if pinned:
            bot_id = (await bot.get_me()).id

            if pinned.from_user.id == bot_id:
                return pinned.message_id

        return None

    except Exception as e:
        await log(
            log_message=f"Ошибка получения закрепленного сообщения в чате {tg_chat_id}: {e}"
        )
        return None
