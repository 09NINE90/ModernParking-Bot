from app.bot import bot
from app.bot.keyboards import back_to_main_markup
from app.logs.log_builder import log, LogType


async def auto_cancel_distribution(tg_id, message_id):
    try:
        new_text = "⏳ <b>Время для выбора расписания истекло.</b>"

        await bot.edit_message_text(
            chat_id=tg_id,
            message_id=message_id,
            text=new_text,
            reply_markup=back_to_main_markup
        )

        await log(
            log_type=LogType.DEBUG,
            log_message=f"Сообщение {message_id} для {tg_id} автоматически отредактировано "
                        f"по истечению времени",
            is_sending_log=False
        )
    except Exception as e:
        await log(
            log_message=f"Ошибка автоматического изменения сообщения пользователя {tg_id}: {e}"
        )
