from datetime import datetime
from typing import Any, Callable
from src.data import ORDER
import signals_rpc.onlexnet.pdt.signals.events as se

Publisher = Callable[[Any], None]

def as_datetime6(value: datetime) -> se.datetime6:
    yyyymmdd = value.year * 10000 + value.month * 100 + value.day
    hhmm = value.hour * 100 + value.minute
    return se.datetime6(yyyymmdd, hhmm)
    
def send(order: ORDER, sender: Publisher, when: datetime) -> None:
    when_dto = as_datetime6(when)
    if order == ORDER.BUY:
        event = se.Order(se.OrderKind.BUY, when_dto)
    elif order == ORDER.SELL:
        event = se.Order(se.OrderKind.SELL, when_dto)
    else:
        return
    sender(event)

