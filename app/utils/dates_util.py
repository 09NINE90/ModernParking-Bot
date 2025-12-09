from datetime import datetime


def get_day_text(rq_date):
    if datetime.today().date() == rq_date:
        return "сегодня"
    else:
        return "завтра"
