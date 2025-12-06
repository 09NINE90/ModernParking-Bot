from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.bot.constants.callback_data import CallbackData
from app.bot.keyboards import main_markup


def setup_base_callbacks(router: Router) -> None:
    """Настройка базовых callback обработчиков"""

    @router.callback_query(F.data == CallbackData.BACK_TO_MAIN)
    async def handle_back_to_main(callback: CallbackQuery):
        """Обработка возврата в главное меню"""
        await callback.message.edit_text(
            "🚗 Бот распределения парковочных мест\n\n"
            "Выберите действие:",
            reply_markup=main_markup
        )
