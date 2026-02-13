from datetime import datetime, timedelta

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.handlers.callbacks.utils.distribution_spots_util import distribute_parking_spots
from app.bot.keyboards import schedule_selection_markup, back_to_main_markup
from app.constants import get_readable_schedule, reverse_day_offsets
from app.data import get_db_connection
from app.logs.log_builder import log, LogType
from app.scheduler.schedule_utils import cancel_schedule_distribute_weekly_parking_schedules
from app.scheduler.scheduler_manager import schedule_distribute_weekly_parking_schedules
from app.services import ServiceFactory
from app.utils.emoji_util import sber_emoji, warn_emoji, date_emoji, sber_date_emoji


async def distribute_weekly_schedules():
    with get_db_connection() as conn:
        spot_requests_schedule_service = ServiceFactory.create_spot_requests_schedule_service(conn)

        result_schedules = spot_requests_schedule_service.get_user_schedules_with_tg_id()

        if len(result_schedules) == 0:
            await log(
                log_type=LogType.DEBUG,
                log_message="Не найдено расписаний на следующую неделю"
            )
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
                f"{sber_date_emoji} <b>Расписание на {dates_range}</b>\n\n"
                f"До конца дня выберите дни для парковки:\n\n"
                f"<i>Автоматически создам запросы на места</i>"
            )

            from app.bot import bot
            sent_message = await bot.send_message(
                chat_id=user_id,
                text=message_text,
                reply_markup=keyboard,
            )

            await schedule_distribute_weekly_parking_schedules(user_id, sent_message.message_id)
        except Exception as e:
            await log(
                log_message=f"Ошибка отправки сообщения для выбора расписания пользователю {user_id}: {e}"
            )


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


async def select_schedule(callback: CallbackQuery, state: FSMContext, schedule_id):
    tg_user_id = callback.from_user.id

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)
        spot_requests_schedule_service = ServiceFactory.create_spot_requests_schedule_service(conn)
        spot_request_service = ServiceFactory.create_spot_request_service(conn)

        db_user_id = user_service.get_db_user_id_by_tg_id(tg_user_id)
        if not db_user_id:
            return None

        result = spot_requests_schedule_service.get_spot_requests_schedule_by_id(
            schedule_id=schedule_id,
        )

        if not result:
            await log(
                log_message=f"Не найдено расписание по ID {schedule_id}"
            )
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
            insert_result = spot_request_service.create_user_spot_request(
                db_user_id=db_user_id,
                request_date=selected_date,
                is_auto_request=True
            )
            weekday_name_ru = reverse_day_offsets[selected_date.weekday()]
            date_str = selected_date.strftime("%d.%m.%Y")

            if not insert_result:
                skipped.append(f"{weekday_name_ru} ({date_str})")
            else:
                created.append(f"{weekday_name_ru} ({date_str})")

        message_parts = []

        if created:
            message_parts.append(f"{sber_emoji} Созданы запросы на:\n" + "\n".join(f"• {d}" for d in created))

        if skipped:
            message_parts.append(
                f"\n{warn_emoji} Уже существовали и были пропущены:\n" + "\n".join(f"• {d}" for d in skipped))

        message_text = "\n".join(message_parts) if message_parts else "Нет дат для создания запросов."

        await cancel_schedule_distribute_weekly_parking_schedules(tg_user_id)

        conn.commit()

        await distribute_parking_spots()

        await callback.message.edit_text(
            text=message_text,
            reply_markup=back_to_main_markup
        )

        return None
