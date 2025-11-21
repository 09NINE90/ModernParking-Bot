from collections import namedtuple
from datetime import datetime, timedelta


def get_current_quarter_and_year() -> str:
    now = datetime.now()
    quarter = (now.month - 1) // 3 + 1
    result = f"{quarter}Q{now.year}"
    return result


def get_previous_quarter_and_year() -> str:
    now = datetime.now()
    current_quarter = (now.month - 1) // 3 + 1
    if current_quarter == 1:
        prev_quarter = 4
        year = now.year - 1
    else:
        prev_quarter = current_quarter - 1
        year = now.year

    return f"{prev_quarter}Q{year}"



def get_first_and_last_quarter_dates(quarter_year):
    quarter = int(quarter_year[0])
    year = int(quarter_year[2:])
    quarter_dates = namedtuple("QuarterDates", ["first_date", "last_date"])
    match quarter:
        case 1:
            first_date = f'{year}-01-01'
            last_date = f'{year}-03-31'
        case 2:
            first_date = f'{year}-04-01'
            last_date = f'{year}-06-30'
        case 3:
            first_date = f'{year}-07-01'
            last_date = f'{year}-09-30'
        case 4:
            first_date = f'{year}-10-01'
            last_date = f'{year}-12-31'
        case _:
            raise ValueError(f"Неверный квартал: {quarter_year}")


    return quarter_dates(first_date, last_date)
