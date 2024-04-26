from datetime import datetime


def from_datetime5(yyyymmddhhmm) -> datetime:
    year = yyyymmddhhmm // 100000000
    month = yyyymmddhhmm // 1000000 % 100
    days = yyyymmddhhmm // 10000 % 100
    hours = yyyymmddhhmm // 100 % 100
    minutes = yyyymmddhhmm % 100
    seconds = 0
    return datetime(year, month, days, hours, minutes, seconds)

def to_datetime5(dt: datetime) -> int:
    year = dt.year * 100000000
    month = dt.month * 1000000
    days = dt.day * 10000
    hours = dt.hour * 100
    minutes = dt.minute
    return year + month + days + hours + minutes

def from_datetime32(yyyymmdd: int , hhmm: int) -> datetime:
    year = yyyymmdd // 10000
    month = yyyymmdd // 100 % 100
    days = yyyymmdd % 100
    hours = hhmm // 100
    minutes = hhmm % 100
    seconds = 0
    return datetime(year, month, days, hours, minutes, seconds)

def to_datetime32(value: datetime) -> tuple[int, int]:
    yyyymmdd = value.year * 1000 + value.month * 100 + value.day
    hhmm = value.hour * 100 + value.minute
    return yyyymmdd, hhmm

