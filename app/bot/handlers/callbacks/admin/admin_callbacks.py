from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.bot.constants.callback_data import CallbackData
from app.bot.handlers.callbacks.admin.utils.clear_tables_util import clear_tables_request, confirm_clear_tables
from app.bot.handlers.callbacks.admin.utils.for_admin_statistics import for_admin_statistics, get_period_stats, \
    show_period_stats_details
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

    @router.callback_query(F.data == CallbackData.CLEAR_TABLES)
    async def clear_tables_callback(callback: CallbackQuery):
        try:
            await clear_tables_request(callback)
        except Exception as e:
            await log(
                log_message=f"Ошибка в clear_tables_callback: {e}"
            )

    @router.callback_query(F.data == CallbackData.YES_CLEAR_TABLES)
    async def confirm_clear_tables_callback(callback: CallbackQuery):
        try:
            await confirm_clear_tables(callback)
        except Exception as e:
            await log(
                log_message=f"Ошибка в confirm_clear_tables_callback: {e}"
            )

    @router.callback_query(F.data.endswith(CallbackData.POSTFIX_STATS))
    async def get_period_stats_callback(callback: CallbackQuery):
        try:
            period_name = callback.data.replace(CallbackData.POSTFIX_STATS, "")
            await get_period_stats(callback, period_name)
        except Exception as e:
            await log(
                log_message=f"Ошибка в confirm_clear_tables_callback: {e}"
            )

    @router.callback_query(
        F.data.regexp(r"^(week|month|quarter|year)_.+(?<!_stats)$")
    )
    async def period_stats_details_callback(callback: CallbackQuery):
        try:
            data = callback.data
            period_name, _, period_display = data.partition("_")
            await show_period_stats_details(callback, period_name, period_display)
        except Exception as e:
            await log(
                log_message=f"Ошибка в period_stats_details_callback: {e}",
            )
