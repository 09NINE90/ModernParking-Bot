import logging
from datetime import datetime

from aiogram import types

from app.bot.keyboard_markup import return_markup
from app.bot.service.statistics_service import statistics_service


async def statistics(message: types.Message):
    try:
        await statistics_service(day=datetime.today())
    except Exception as e:
        logging.error(f"Error checking statistics: {e}")
        await message.answer(
            "❌ Произошла ошибка при получении статистики. Попробуйте позже.",
            reply_markup=return_markup
        )

