from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.bot.constants.callback_data import CallbackData
from app.bot.handlers.callbacks.admin.utils.for_admin_statistics import for_admin_statistics
from app.bot.keyboards import main_admin_markup
from app.logs.log_builder import log


def setup_admin_callbacks(router: Router) -> None:
    """Настройка callback обработчиков для админа"""

    @router.callback_query(F.data == CallbackData.MAIN_ADMIN)
    async def main_admin_callback(callback: CallbackQuery):
        try:
            await callback.message.edit_text(
                text="Административная панель Бота-Ассистента парковки",
                reply_markup=main_admin_markup
            )
        except Exception as e:
            await log(
                log_message=f"Ошибка перехода в main_admin_callback: {e}"
            )

    @router.callback_query(F.data == CallbackData.ALL_STATISTICS)
    async def all_statistics_callback(callback: CallbackQuery):
        try:
            await for_admin_statistics(callback)
        except Exception as e:
            await log(
                log_message=f"Ошибка в all_statistics_callback: {e}"
            )
