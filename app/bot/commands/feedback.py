from aiogram import types

from app.bot.config import GROUP_ID
from app.bot.keyboard_markup import feedback_markup


async def feedback(message: types.Message):
    if message.chat.id == GROUP_ID:
        return
    await message.answer(
        text="🤖 <b>Обратная связь по боту-ассистенту парковки</b>",
        reply_markup=feedback_markup
    )