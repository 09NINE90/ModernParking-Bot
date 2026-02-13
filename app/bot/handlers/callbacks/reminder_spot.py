from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.bot.constants.callback_data import CallbackData
from app.bot.handlers.callbacks.utils.confirmations.reminder_spot_util import take_spot_by_reminder, \
    cancel_spot_by_reminder
from app.bot.keyboards import back_to_main_markup
from app.logs.log_builder import log
from app.utils.emoji_util import canceled_emoji


def setup_reminder_spot_callbacks(router: Router) -> None:
    @router.callback_query(F.data == CallbackData.TAKE_SPOT_BY_REMINDER)
    async def take_spot_by_reminder_callback(callback: CallbackQuery):
        """
            Подтверждение занятого места
        """
        try:
            await take_spot_by_reminder(callback)
        except Exception as e:
            await callback.message.edit_text(
                text=f"{canceled_emoji} Ошибка подтверждения занятого места\n\n"
                     "<i>Обратитесь к администратору.\nВызовете:/feedback </i>",
                reply_markup=back_to_main_markup
            )
            await log(
                log_message=f"Ошибка подтверждения занятого места: {e}"
            )

    @router.callback_query(F.data == CallbackData.CANCEL_SPOT_BY_REMINDER)
    async def cancel_spot_by_reminder_callback(callback: CallbackQuery):
        """
            Отказ от занятого места
        """
        try:
            await cancel_spot_by_reminder(callback)
        except Exception as e:
            await callback.message.edit_text(
                text=f"{canceled_emoji} Ошибка отказа от занятого места\n\n"
                     "<i>Обратитесь к администратору.\nВызовете:/feedback </i>",
                reply_markup=back_to_main_markup
            )
            await log(
                log_message=f"Ошибка подтверждения занятого места: {e}"
            )