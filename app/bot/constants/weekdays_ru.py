weekdays_ru = {
    0: "Пн", 1: "Вт",
    2: "Ср", 3: "Чт",
    4: "Пт", 5: "Сб",
    6: "Вс"
}

full_weekdays_ru = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница"
]

day_offsets = {
    "Понедельник": 0,
    "Вторник": 1,
    "Среда": 2,
    "Четверг": 3,
    "Пятница": 4,
    "Суббота": 5,
    "Воскресенье": 6
}

reverse_day_offsets = {v: k for k, v in day_offsets.items()}


def sort_weekdays(days_list):
    """
        Сортирует дни недели по порядку
    """
    return sorted(days_list, key=lambda day: day_offsets.get(day, 999))


def get_day_numbers_for_week_days(days_list):
    """Возвращает номера для дней недели из списка"""
    return ",".join(str(day_offsets[day]) for day in days_list)

def get_week_days_for_day_numbers(day_numbers):
    """Возвращает номера для дней недели из списка"""
    days = day_numbers.split(',')
    return ", ".join(reverse_day_offsets[int(day_number)] for day_number in days)