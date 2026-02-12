from aiogram.types import CallbackQuery

from app.bot.keyboards import confirm_clear_tables_admin, back_to_main_admin
from app.config import settings
from app.data import get_db_connection
from app.services import ServiceFactory
from app.utils.emoji_util import warn_emoji


async def clear_tables_request(callback: CallbackQuery):
    tg_user_id = callback.from_user.id

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)

        is_admin = user_service.is_user_admin(tg_user_id)
        if not is_admin:
            await callback.message.edit_text(
                text=f"{warn_emoji} Вы не админ!",
            )
            return None

    current_db_schema = settings.DB_SCHEMA
    await callback.message.edit_text(
        text=f"{warn_emoji} Вы уверены, что хотите почистить "
             f"таблицы в схеме: <b>{current_db_schema}</b>?",
        reply_markup=confirm_clear_tables_admin
    )

    return None


async def confirm_clear_tables(callback: CallbackQuery):
    tg_user_id = callback.from_user.id

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)
        admin_service = ServiceFactory.create_admin_service(conn)

        is_admin = user_service.is_user_admin(tg_user_id)
        if not is_admin:
            await callback.message.edit_text(
                text=f"{warn_emoji} Вы не админ!",
            )
            return None

        result = admin_service.clear_tables()

        conn.commit()

    if not result:
        message_text = f"{warn_emoji} Ошибка при очистке таблиц. Подробности в логах."
    else:
        message_text = (
            "<b>Удалено строк:</b>\n\n"
            f"Таблица подтверждений: <b>{result['spot_confirmations']}</b>\n"
            f"Таблица напоминаний: <b>{result['reminder_spot_confirmations']}</b>\n"
            f"Таблица запросов: <b>{result['parking_requests']}</b>\n"
            f"Таблица освобождений: <b>{result['parking_releases']}</b>"
        )

    await callback.message.edit_text(
        text=message_text,
        reply_markup=back_to_main_admin
    )

    return None
