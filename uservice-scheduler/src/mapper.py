from datetime import datetime
import scheduler_rpc.schema_pb2 as proto
import scheduler_rpc.onlexnet.ptn.scheduler.events as events


def from_dto(x: events.NewTime) -> datetime:
    as_year = x.yyyymmdd // 10000
    as_month = x.yyyymmdd // 100 % 100
    as_days = x.yyyymmdd % 100
    as_hours = x.hhmm // 100
    as_minutes = x.hhmm % 100
    as_seconds = 0
    return datetime(as_year, as_month, as_days, as_hours, as_minutes, as_seconds)

def to_dto(x: datetime, correlation_id: str) -> events.NewTime:
    yyyymmdd = x.year * 10000 + x.month * 100 + x.day
    hhmm = x.hour * 100 + x.minute
    return events.NewTime(correlationId=correlation_id, yyyymmdd=yyyymmdd, hhmm = hhmm)

def normalize(it: datetime) -> datetime:
    as_dto = to_dto(it, "ignored")
    return from_dto(as_dto)
