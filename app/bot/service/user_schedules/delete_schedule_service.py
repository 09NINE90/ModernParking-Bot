import logging

import psycopg2
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.constants.log_types import LogNotification
from app.bot.constants.weekdays_ru import get_week_days_for_day_numbers
from app.bot.keyboard_markup import return_markup, create_delete_schedules_keyboard, \
    confirmation_delete_schedule_markup, back_to_delete_default_schedule_markup
from app.bot.notification.log_notification import send_log_notification
from app.bot.service.user_service import get_db_user_id
from app.data.init_db import get_db_connection
from app.data.repository.spot_requests_schedule_repository import get_spot_requests_schedule_by_user_with_id, \
    get_spot_requests_schedule_by_id, delete_spot_requests_schedule_by_id
from app.log_text import DB_USER_ID_GET_ERROR, DATABASE_ERROR


async def delete_default_schedule(query: CallbackQuery, state: FSMContext):
    tg_user_id = query.from_user.id

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                db_user_id = await get_db_user_id(cur, tg_user_id)

                if not db_user_id:
                    logging.error(DB_USER_ID_GET_ERROR.format(tg_user_id))
                    await send_log_notification(LogNotification.ERROR, DB_USER_ID_GET_ERROR.format(tg_user_id))
                    return None

                result_list = await get_spot_requests_schedule_by_user_with_id(cur, db_user_id)

                if result_list:
                    keyboard = create_delete_schedules_keyboard(result_list)

                    message_text = ("🗑️ <b>Удаление расписания</b>\n\n"
                                    "Выберите расписание для удаления:")

                    await query.message.edit_text(
                        text=message_text,
                        reply_markup=keyboard
                    )
                else:
                    await query.message.edit_text(
                        text="👀 У вас нет сохраненных расписаний для удаления.",
                        reply_markup=return_markup
                    )

    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))


async def confirmation_delete_schedule_by_id(query: CallbackQuery, state: FSMContext, schedule_id: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                result = await get_spot_requests_schedule_by_id(cur, schedule_id)
                week_days = get_week_days_for_day_numbers(result.day_numbers)
                message_text = f"🗑️ Уверены, что хотите удалить расписание на: <b>{week_days}</b>?"

                await query.message.edit_text(
                    text=message_text,
                    reply_markup=confirmation_delete_schedule_markup(result.id)
                )

    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))


async def delete_schedule_by_id(query: CallbackQuery, state: FSMContext, schedule_id: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                is_delete = await delete_spot_requests_schedule_by_id(cur, schedule_id)

                if is_delete:
                    message_text = "Расписание успешно удалено"
                    await query.message.edit_text(
                        text=message_text,
                        reply_markup=back_to_delete_default_schedule_markup
                    )
                else:
                    message_text = "Что-то пошло не так..."
                    await query.message.edit_text(
                        text=message_text,
                        reply_markup=back_to_delete_default_schedule_markup
                    )

    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))
