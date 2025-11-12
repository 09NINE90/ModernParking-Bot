from aiogram.types import CallbackQuery

from app.bot.keyboard_markup import main_markup


async def back_to_main_menu(query: CallbackQuery):
    """Возврат в главное меню"""

    await query.message.edit_text(
        "🚗 Бот распределения парковочных мест\n\n"
        "Выберите действие:",
        reply_markup=main_markup
    )
