import logging

from aiogram import types

from app.bot.keyboard_markup import return_markup
from app.bot.service.statistics_service import daily_statistics_service
from app.log_text import STATISTICS_CHECK_ERROR


async def statistics(message: types.Message):
    try:
        await daily_statistics_service()
    except Exception as e:
        logging.error(STATISTICS_CHECK_ERROR.format(e))
        await message.answer(
            "❌ Произошла ошибка при получении статистики. Попробуйте позже.",
            reply_markup=return_markup
        )

