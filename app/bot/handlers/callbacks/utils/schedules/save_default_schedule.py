from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.keyboards import success_save_default_schedule_markup
from app.bot.keyboards.inline import back_to_create_default_schedule_markup
from app.constants import sort_weekdays, get_day_numbers_for_week_days, reverse_day_offsets, weekdays_ru
from app.data import get_db_connection
from app.services import ServiceFactory


async def save_default_schedule(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_days = data.get('selected_days', [])

    tg_user_id = callback.from_user.id

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)
        spot_requests_schedule_service = ServiceFactory.create_spot_requests_schedule_service(conn)

        db_user_id = user_service.get_db_user_id_by_tg_id(tg_user_id)
        if not db_user_id:
            return None

        sorted_days = sort_weekdays(selected_days)
        day_numbers_for_week_days = get_day_numbers_for_week_days(sorted_days)

        success_id = spot_requests_schedule_service.add_spot_requests_schedule(
            user_id=db_user_id,
            day_numbers=day_numbers_for_week_days
        )

        days_text = ", ".join(sorted_days)
        if success_id:
            result_list = spot_requests_schedule_service.get_spot_requests_schedule_by_user(
                user_id=db_user_id,
            )

            user_schedules = get_user_schedules(result_list)

            message_text = (f"✅ Сохранил расписание на: <b>{days_text}</b>\n\n"
                            f"Ваши актуальные расписания:\n"
                            f"<b>• {user_schedules}\n\n</b>"
                            f"В воскресение ждите подтверждения расписания")
            await callback.message.edit_text(
                text=message_text,
                reply_markup=success_save_default_schedule_markup
            )
        else:
            message_text = f"У Вас уже есть расписание на: <b>{days_text}</b>"
            await callback.message.edit_text(
                text=message_text,
                reply_markup=back_to_create_default_schedule_markup
            )

        await state.clear()
        return None


def get_user_schedules(result_list: list[str]):
    """
        Преобразует список числовых расписаний в читаемые строки дней недели.

        Args:
            result_list: Список строк с числовыми кодами дней через запятую
                       (например, ['1,3,5', '2,4,6'])

        Returns:
            Строка с расписаниями, где каждая строка содержит названия дней недели,
            разделенные запятыми, а расписания разделены переносами строк.

        Example:
            Вход: ['1,3,5', '2,4,6']
            Выход: "Вторник, Четверг, Пятница\nСреда, Пятница, Суббота"
    """
    result_lines = []

    for user_schedule in result_list:
        schedule: list[str] = user_schedule.split(',')
        day_names = []

        for day_number_str in schedule:
            day_number = int(day_number_str.strip())
            day_name = reverse_day_offsets.get(day_number)
            if day_name:
                day_names.append(day_name)

        result_lines.append(', '.join(day_names))

    return '\n• '.join(result_lines)


def get_readable_schedule(day_numbers: str) -> str:
    """Преобразует числовые коды дней в читаемые названия"""
    days = day_numbers.split(',')
    readable_days = [weekdays_ru.get(int(day.strip()), day) for day in days]
    return ', '.join(readable_days)
