import os
from datetime import datetime

ade_start_date = None


def calculate_week(date: str):
    global ade_start_date
    if ade_start_date is None:
        ade_start_date = datetime.strptime(os.environ.get("ADE_START_DATE"), "%Y%m%d")

    date_format = "%Y%m%d"
    date = datetime.strptime(date, date_format)

    delta = date - ade_start_date
    return delta.days // 7


def calculate_day_id(date: str):
    # Monday is 0 and Sunday is 6.
    global ade_start_date
    if ade_start_date is None:
        ade_start_date = datetime.strptime(os.environ.get("ADE_START_DATE"), "%Y%m%d")

    date_format = "%Y%m%d"
    date = datetime.strptime(date, date_format)
    return date.weekday()