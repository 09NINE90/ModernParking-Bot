import logging

from aiogram import types

from app.bot.config import GROUP_ID
from app.bot.keyboard_markup import return_markup
from app.bot.service.statistics_service import weekly_statistics_service
from app.log_text import STATISTICS_CHECK_ERROR


async def weekly_statistics(message: types.Message):
    if message.chat.id == GROUP_ID:
        return
    try:
        await weekly_statistics_service()
    except Exception as e:
        logging.error(STATISTICS_CHECK_ERROR.format(e))
        await message.answer(
            "❌ Произошла ошибка при получении статистики. Попробуйте позже.",
            reply_markup=return_markup
        )
