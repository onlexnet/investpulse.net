from typing import Any, Callable
from src.data import ORDER
import signals_rpc.onlexnet.pdt.signals.events as se

Publisher = Callable[[Any], None]

def send(order: ORDER, sender: Publisher) -> None:
    if order == ORDER.BUY:
        event = se.Order(se.OrderKind.BUY)
    elif order == ORDER.SELL:
        event = se.Order(se.OrderKind.SELL)
    else:
        return
    sender(event)
    