import logging
from datetime import datetime, timedelta

import psycopg2
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.config import bot
from app.bot.constants.log_types import LogNotification
from app.bot.constants.weekdays_ru import reverse_day_offsets
from app.bot.keyboard_markup import schedule_selection_markup, return_markup
from app.bot.notification.log_notification import send_log_notification
from app.bot.service.distribution_service import distribute_parking_spots
from app.bot.service.user_schedules.schedules_service import get_readable_schedule
from app.bot.service.user_service import get_db_user_id
from app.data.init_db import get_db_connection
from app.data.repository.parking_requests_repository import insert_request_on_date
from app.data.repository.spot_requests_schedule_repository import get_user_schedules_with_tg_id, \
    get_spot_requests_schedule_by_id
from app.log_text import DATABASE_ERROR, DB_USER_ID_GET_ERROR
from app.schedule.schedule_utils import cancel_schedule_distribute_weekly_parking_schedules
from app.schedule.scheduler_manager import schedule_distribute_weekly_parking_schedules


async def distribute_weekly_parking_schedules():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:

                result_schedules = await get_user_schedules_with_tg_id(cur)
                if not result_schedules:
                    logging.info(f"Not found schedules on next week")
                    await send_log_notification(LogNotification.INFO, "Not found schedules on next week")
                    return

                result = {}
                for tg_id, schedules in result_schedules.items():
                    user_schedules = []

                    for schedule in schedules:
                        transformed_schedule = {
                            'id': schedule.id,
                            'day_numbers': schedule.day_numbers,
                            'short_day_names': get_readable_schedule(schedule.day_numbers)
                        }
                        user_schedules.append(transformed_schedule)

                    result[tg_id] = user_schedules

                await send_schedule_selection(result)
    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))


async def send_schedule_selection(schedule_data: dict):
    """
        Рассылка расписаний пользователям
    """
    next_week_dates = get_next_work_week_dates()
    dates_range = format_week_dates_range(next_week_dates)

    for user_id, schedules in schedule_data.items():
        try:
            keyboard = schedule_selection_markup(schedules)

            message_text = (
                f"📅 <b>Расписание на {dates_range}</b>\n\n"
                f"До конца дня выберите дни для парковки:\n\n"
                f"<i>Автоматически создам запросы на места</i>"
            )

            sent_message = await bot.send_message(
                chat_id=user_id,
                text=message_text,
                reply_markup=keyboard,
            )

            await schedule_distribute_weekly_parking_schedules(user_id, sent_message.message_id)
        except Exception as e:
            logging.error(f"Failed to send schedule to {user_id}: {e}")


def get_next_work_week_dates():
    """
        Возвращает даты следующей рабочей недели (понедельник-пятница)
    """
    today = datetime.now().date()

    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7

    next_monday = today + timedelta(days=days_until_monday)

    week_dates = []
    for i in range(5):
        week_date = next_monday + timedelta(days=i)
        week_dates.append(week_date)

    return week_dates


def format_week_dates_range(week_dates):
    """
        Форматирует диапазон дат для отображения
    """
    if not week_dates:
        return ""

    start_date = week_dates[0]
    end_date = week_dates[-1]

    date_format = "%d.%m"
    return f"{start_date.strftime(date_format)} - {end_date.strftime(date_format)}"


async def select_schedule(query: CallbackQuery, state: FSMContext, schedule_id):
    tg_user_id = query.from_user.id
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:

                db_user_id = await get_db_user_id(cur, tg_user_id)

                if not db_user_id:
                    logging.error(DB_USER_ID_GET_ERROR.format(tg_user_id))
                    await send_log_notification(LogNotification.ERROR, DB_USER_ID_GET_ERROR.format(tg_user_id))
                    return None

                result = await get_spot_requests_schedule_by_id(cur, schedule_id)
                if not result:
                    logging.error(f"Error Not found schedule by id {schedule_id}")
                    await send_log_notification(LogNotification.ERROR,
                                                f"Error Not found schedule by id {schedule_id}")
                    return None

                schedule_days = result.day_numbers.split(',')
                next_week_dates = get_next_work_week_dates()

                selected_dates = []
                for day_index in schedule_days:
                    index = int(day_index)
                    if index < len(next_week_dates):
                        selected_dates.append(next_week_dates[index])

                created = []
                skipped = []
                for selected_date in selected_dates:
                    insert_result = await insert_request_on_date(cur, db_user_id, selected_date)
                    weekday_name_ru = reverse_day_offsets[selected_date.weekday()]
                    date_str = selected_date.strftime("%d.%m.%Y")

                    if insert_result is None:
                        skipped.append(f"{weekday_name_ru} ({date_str})")
                        logging.debug(f"Запрос на {selected_date} уже существует, пропускаю.")
                    else:
                        created.append(f"{weekday_name_ru} ({date_str})")

                message_parts = []

                if created:
                    message_parts.append("✅ Созданы запросы на:\n" + "\n".join(f"• {d}" for d in created))

                if skipped:
                    message_parts.append(
                        "\n⚠️ Уже существовали и были пропущены:\n" + "\n".join(f"• {d}" for d in skipped))

                message_text = "\n".join(message_parts) if message_parts else "Нет дат для создания запросов."

                await cancel_schedule_distribute_weekly_parking_schedules(tg_user_id)

                conn.commit()
                await distribute_parking_spots()

                await query.message.edit_text(
                    text=message_text,
                    reply_markup=return_markup
                )

    except psycopg2.Error as e:
        logging.error(DATABASE_ERROR.format(e))
        await send_log_notification(LogNotification.ERROR, DATABASE_ERROR.format(e))
