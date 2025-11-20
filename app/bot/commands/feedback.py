from aiogram import types

from app.bot.keyboard_markup import feedback_markup


async def feedback(message: types.Message):
    await message.answer(
        text="🤖 <b>Обратная связь по боту-ассистенту парковки</b>",
        reply_markup=feedback_markup
    )