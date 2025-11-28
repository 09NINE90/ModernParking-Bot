import logging

import psycopg2
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.constants.log_types import LogNotification
from app.bot.constants.weekdays_ru import sort_weekdays, get_day_numbers_for_week_days
from app.bot.keyboard_markup import back_to_create_default_schedule_markup, success_save_default_schedule_markup
from app.bot.notification.log_notification import send_log_notification
from app.bot.service.user_schedules.schedules_service import get_user_schedules
from app.bot.service.user_service import get_db_user_id
from app.data.init_db import get_db_connection
from app.data.repository.spot_requests_schedule_repository import add_spot_requests_schedule, \
    get_spot_requests_schedule_by_user
from app.log_text import DB_USER_ID_GET_ERROR, DATABASE_ERROR


async def save_schedule(query: CallbackQuery, state: FSMContext, selected_days: list = None):
    tg_user_id = query.from_user.id

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                db_user_id = await get_db_user_id(cur, tg_user_id)

                if not db_user_id:
                    logging.error(DB_USER_ID_GET_ERROR.format(tg_user_id))
                    await send_log_notification(LogNotification.ERROR, DB_USER_ID_GET_ERROR.format(tg_user_id))
                    return None

                sorted_days = sort_weekdays(selected_days)
                day_numbers_for_week_days = get_day_numbers_for_week_days(sorted_days)

                success_id = await add_spot_requests_schedule(cur, db_user_id, day_numbers_for_week_days)

                days_text = ", ".join(sorted_days)
                if success_id:

                    result_list = await get_spot_requests_schedule_by_user(cur, db_user_id)
                    user_schedules = get_user_schedules(result_list)

                    days_text = ", ".join(sorted_days)

                    message_text = (f"✅ Сохранил расписание на: <b>{days_text}</b>\n\n"
                                    f"Ваши актуальные расписания:\n"
                                    f"<b>• {user_schedules}\n\n</b>"
                                    f"В воскресение ждите подтверждения расписания")
                    await query.message.edit_text(
                        text=message_text,
                        reply_markup=success_save_default_schedule_markup
                    )
                else:
                    message_text = f"У Вас уже есть расписание на: <b>{days_text}</b>"
                    await query.message.edit_text(
                        text=message_text,
                        reply_markup=back_to_create_default_schedule_markup
                    )

    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))
    finally:
        await state.clear()



