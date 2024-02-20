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
    side: Side
    amount: int

# Naive and simple agent to execute requested operations on a Market.
# TODO: allow buy 
# TODO: allow sell
class MarketAgent:
    _budget: float
    _orderbook: Dict[asset_name, Order] = { }
    _listeners: List[Callable[[OrderExecuted], None]] = [ ]
    
    def make_order(self, side: Side, amount: int, date: date):
        for l in self._listeners:
            executed_order = OrderExecuted(side, amount)
            l(executed_order)
    
    # remove listener will be implemented later on, when required
    def add_listener(self, listener: Callable[[OrderExecuted], None]):
        self._listeners.append(listener)

