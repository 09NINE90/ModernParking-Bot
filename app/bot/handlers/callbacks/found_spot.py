from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.bot.constants.callback_data import CallbackData
from app.bot.handlers.callbacks.utils.confirmations.cancel_spot_util import cancel_spot
from app.bot.handlers.callbacks.utils.confirmations.take_spot_util import take_spot
from app.bot.keyboards import back_to_main_markup
from app.logs.log_builder import log
from app.utils.emoji_util import canceled_emoji


def setup_found_spot_callbacks(router: Router) -> None:
    @router.callback_query(F.data == CallbackData.TAKE_SPOT)
    async def take_spot_callback(callback: CallbackQuery):
        """
            Принять предложенное место
        """
        try:
            await take_spot(callback)
        except Exception as e:
            await callback.message.edit_text(
                text=f"{canceled_emoji} Ошибка принятия предложенного места"
                     "<i>Обратитесь к администратору.\nВызовете:/feedback </i>",
                reply_markup=back_to_main_markup
            )
            await log(
                log_message=f"Ошибка в take_spot_callback: {e}"
            )

    @router.callback_query(F.data == CallbackData.CANCEL_SPOT)
    async def cancel_spot_callback(callback: CallbackQuery):
        """
            Отказаться от предложенного места
        """
        try:
            await cancel_spot(callback)
        except Exception as e:
            await callback.message.edit_text(
                text=f"{canceled_emoji} Ошибка отказа от предложенного места"
                     "<i>Обратитесь к администратору.\nВызовете:/feedback </i>",
                reply_markup=back_to_main_markup
            )
            await log(
                log_message=f"Ошибка в cancel_spot_callback: {e}"
            )
