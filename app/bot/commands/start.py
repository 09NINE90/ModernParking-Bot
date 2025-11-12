from aiogram import types

from app.bot.callbacks.register_user import register_user
from app.bot.constants.group_id import GROUP_ID
from app.bot.keyboard_markup import main_markup

async def start(message: types.Message):
    if message.chat.id == GROUP_ID:
        return
    user = message.from_user
    await register_user(user)

    await message.answer(
        "🚗 Бот распределения парковочных мест\n\n"
        "Выберите действие:",
        reply_markup=main_markup
    )