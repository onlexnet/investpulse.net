from datetime import datetime


def from_datetime5(yyyymmdd: int, hhmm: int) -> datetime:
    year = yyyymmdd // 10000
    month = yyyymmdd // 100 % 100
    days = yyyymmdd % 100
    hours = hhmm // 100
    minutes = hhmm % 100
    seconds = 0
    return datetime(year, month, days, hours, minutes, seconds)

def to_datetime5(value: datetime) -> tuple[int, int]:
    yyyymmdd = value.year * 1000 + value.month * 100 + value.day
    hhmm = value.hour * 100 + value.minute
    return yyyymmdd, hhmm

