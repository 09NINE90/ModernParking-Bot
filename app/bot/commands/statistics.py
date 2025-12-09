import logging

import psycopg2
from aiogram import types

from app.bot.constants.log_types import LogNotification
from app.bot.keyboard_markup import return_markup
from app.bot.notification.log_notification import send_log_notification
from app.bot.service.statistics_service import for_admin_statistics
from app.data.init_db import get_db_connection
from app.data.models.users.user_roles import UserRoles
from app.data.repository.users_repository import is_user_has_role
from app.log_text import STATISTICS_CHECK_ERROR, DATABASE_ERROR


async def statistics(message: types.Message):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                is_has_role: bool = await is_user_has_role(cur, message.from_user.id, UserRoles.ADMIN)
                if is_has_role:
                    try:
                        await for_admin_statistics(message)
                    except Exception as e:
                        logging.error(STATISTICS_CHECK_ERROR.format(e))
                        await message.answer(
                            "❌ Произошла ошибка при получении статистики. Попробуйте позже.",
                            reply_markup=return_markup
                        )
                else:
                    return
    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))
