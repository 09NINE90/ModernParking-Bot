import logging

from aiogram import types

from app.bot.callbacks.register_user import register_user
from app.bot.constants.group_id import GROUP_ID
from app.bot.keyboard_markup import main_markup
from app.bot.users.is_user_in_chat import is_user_in_chat


async def start(message: types.Message):
    if message.chat.id == GROUP_ID:
        return
    user = message.from_user

    is_valid_user = await is_user_in_chat(user.id, GROUP_ID)
    if is_valid_user:
        await register_user(user)
    else:
        logging.warn(f"User {user.id} is not in the chat")
        await message.answer("😔 Вам нельзя пользоваться этим ботом, так как вы не состоите в чате парковки офиса")
    await message.answer(
        "🚗 Бот распределения парковочных мест\n\n"
        "Выберите действие:",
        reply_markup=main_markup
    )