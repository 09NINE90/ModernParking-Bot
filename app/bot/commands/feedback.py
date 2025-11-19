from aiogram import types

from app.bot.keyboard_markup import back_markup


async def feedback(message: types.Message):
    await message.answer(
        text="Здесь вы сможете оставлять обратную связь по работе бота\n"
             "Скоро добавим",
        reply_markup=back_markup
    )