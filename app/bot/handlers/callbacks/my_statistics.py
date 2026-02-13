from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.bot.constants.callback_data import CallbackData
from app.bot.handlers.callbacks.utils.my_statistics_util import get_my_statistics
from app.bot.keyboards import back_to_main_markup
from app.logs.log_builder import log
from app.utils.emoji_util import canceled_emoji


def setup_statistics_callbacks(router: Router) -> None:
    @router.callback_query(F.data == CallbackData.MY_STATISTICS)
    async def my_statistics_callback(callback: CallbackQuery):
        """
            Получение статистики пользователя
        """
        try:
            await get_my_statistics(callback)
        except Exception as e:
            await callback.message.edit_text(
                text=f"{canceled_emoji} Ошибка получения статистики"
                     "<i>Обратитесь к администратору.\nВызовете:/feedback </i>",
                reply_markup=back_to_main_markup
            )
            await log(
                log_message=f"Ошибка в my_statistics_callback: {e}"
            )
