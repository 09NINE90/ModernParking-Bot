from aiogram import types

from app.bot.keyboards import main_admin_markup
from app.data import get_db_connection
from app.services import ServiceFactory


async def admin_command(message: types.Message):
    tg_user_id = message.from_user.id

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)

        is_admin = user_service.is_user_admin(tg_user_id)
        if not is_admin:
            return None

        await message.answer(
            text="Административная панель Бота-Ассистента парковки",
            reply_markup=main_admin_markup
        )

        return None
