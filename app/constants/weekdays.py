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

def get_readable_schedule(day_numbers: str) -> str:
    """Преобразует числовые коды дней в читаемые названия"""
    days = day_numbers.split(',')
    readable_days = [weekdays_ru.get(int(day.strip()), day) for day in days]
    return ', '.join(readable_days)