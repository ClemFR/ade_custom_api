from datetime import datetime
import settings

ade_start_date = datetime.strptime(settings.env.get("ADE_START_DATE"), "%Y%m%d")


def calculate_week(date: str):
    date_format = "%Y%m%d"
    date = datetime.strptime(date, date_format)

    delta = date - ade_start_date
    return delta.days // 7


def calculate_day_id(date: str):
    # Monday is 0 and Sunday is 6.
    date_format = "%Y%m%d"
    date = datetime.strptime(date, date_format)
    return date.weekday()
