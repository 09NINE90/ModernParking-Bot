from aiogram import types

from app.bot.keyboards import feedback_markup
from app.config import settings
from app.data import get_db_connection
from app.logs.log_builder import log, LogType
from app.services import ServiceFactory
from app.services.user_service import UserService
from app.utils.emoji_util import sber_black_logo_emoji


async def feedback_command(message: types.Message):
    if message.chat.id == settings.GROUP_ID:
        return
    user = message.from_user

    has_access = await UserService.is_user_in_chat(
        user.id,
        settings.GROUP_ID
    )

    if not has_access:
        await log(
            log_type=LogType.WARN,
            log_message=f"Попытка доступа без прав: {user.id} (@{user.username})"
        )
        await message.answer(
            "😔 Вам нельзя пользоваться этим ботом, "
            "так как Вы не состоите в чате парковки офиса."
        )
        return

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)

        registered = user_service.register_user(user)

        if registered:
            await message.answer(
                text=f"{sber_black_logo_emoji} <b>Обратная связь по боту-ассистенту парковки</b>",
                reply_markup=feedback_markup
            )
        else:
            await log(log_message=f"Ошибка регистрации пользователя: {user.id}")
            await message.answer(
                "❌ Произошла ошибка при регистрации.\n"
                "Пожалуйста, попробуйте позже."
            )