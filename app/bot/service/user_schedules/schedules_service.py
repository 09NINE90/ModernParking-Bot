from app.bot.constants.weekdays_ru import reverse_day_offsets, weekdays_ru
from app.data.models.schedule_dto import ScheduleDto


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
