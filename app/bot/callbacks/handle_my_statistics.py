import logging

from aiogram.types import CallbackQuery

from app.bot.config import GROUP_ID
from app.bot.keyboard_markup import return_markup
from app.bot.service.statistics_service import my_statistics


async def handle_my_statistics(query: CallbackQuery):
    """Обработка вызова статистики пользователя"""
    if query.message.chat.id == GROUP_ID:
        return
    try:
        await my_statistics(query)
    except Exception as e:
        logging.error(f"Error checking statistics: {e}")
        await query.answer(
            "❌ Произошла ошибка при получении статистики. Попробуйте позже.",
            reply_markup=return_markup
        )