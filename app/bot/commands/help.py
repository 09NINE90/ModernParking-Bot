from aiogram import types

from app.bot.keyboard_markup import back_markup


async def help_command(message: types.Message):
    await message.answer(
        text="Здесь будет детальная инструкция по работе бота\n"
             "Скоро добавим",
        reply_markup=back_markup
    )