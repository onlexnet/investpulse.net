from abc import ABC, abstractmethod
from datetime import date
from enum import Enum
from typing import Callable, Dict, List

from attr import dataclass

asset_name = str

class Side(Enum):
    BUY = 'BUY'
    SELL = 'SELL'
    

@dataclass
class Order:
    side: Side
    amount: int


@dataclass
class OrderExecuted:
    # Positive values mean: BUY, negative values mean: SELL
    side: Side
    amount: int
    total_price: float

# Naive and simple agent to execute requested operations on a Market.
# TODO: allow buy 
# TODO: allow sell
class MarketAgent:
    _budget: float
    _orderbook: Dict[asset_name, Order] = { }
    _listeners: List[Callable[[OrderExecuted], None]] = [ ]
    
    # TODO remove suggested price as Agent should be aware what is the best price, and include additional operational costs related to buy/sell oeprations
    def make_order(self, side: Side, amount: int, date: date, suggested_price: float):
        assert amount > 0
        for l in self._listeners:
            executed_order = OrderExecuted(side, amount, suggested_price)
            l(executed_order)
    
    # remove listener will be implemented later on, when required
    def add_listener(self, listener: Callable[[OrderExecuted], None]):
        self._listeners.append(listener)

