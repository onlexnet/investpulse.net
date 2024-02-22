from abc import ABC, abstractmethod
from datetime import date
from enum import Enum
import math
from typing import Callable, Dict, List, Union, cast

from attr import dataclass
from pydantic import InstanceOf

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

class AmountOptions(Enum):
    MAX = 'MAX'

AmountOrInt = Union[int, AmountOptions]

# Naive and simple agent to execute requested operations on a Market.
# TODO: allow buy 
# TODO: allow sell
class MarketAgent:
    """
    - TODO: Budget size control based on initial payment and subsequent top-ups.
    - TODO: Buying assets, but net exceeding available budget
    - TODO: Selling assets, but no exceeding what is owned
    - TODO: remove suggested_proce as agebt should be avare what the best proce is
    - TODO: Incorporate the spread into cost calculations
    - ? Retry unrealized buy / sell orders as long as there is not opposite request
    """
    _budget: float
    _orderbook: Dict[asset_name, Order] = { }
    _assets:Dict[asset_name, int] # number of controlled assets
    _listeners: List[Callable[[OrderExecuted], None]] = [ ]
    
    def __init__(self, budget: float = 0, controlled_assets: Dict[asset_name, int] = { }):
        self._budget = budget
        self._assets = controlled_assets
                
    # TODO remove suggested price as Agent should be aware what is the best price, and include additional operational costs related to buy/sell oeprations
    def make_order(self, side: Side, amount: AmountOrInt, date: date, suggested_price: float):
        
        asset_name = 'msft' # TODO move such param to proper place after making solution multi-asset
        
        # Calculate real number of asset to buy / sell
        assets_delta: int = 0
        if isinstance(amount, int):
            assets_delta = cast(int, amount)
        elif isinstance(amount, AmountOptions):
            amount_option = cast(AmountOptions, amount)
            if amount_option == AmountOptions.MAX:
                if side == Side.BUY:
                    assets_delta = math.floor(self._budget / suggested_price)
                elif side == Side.SELL:
                    assets_delta = self._assets.get(asset_name, 0)
                else:
                    raise ValueError(f"Invalid Side:{side}")
            else:
                raise ValueError(f"Invalid AmountOption:{amount_option}")
                
        # here real synchronous market operation TODO
        
        # apply side effects of the operation
        assets = self._assets.get(asset_name, 0)
        assets_signed_delta = assets_delta if side == Side.BUY else -assets_delta
        budget_signed_delta = -assets_signed_delta * suggested_price
        
        new_assets = assets + assets_signed_delta
        new_budget = round(self._budget + budget_signed_delta, 2)
        self._assets[asset_name] = new_assets
        self._budget = new_budget
        
        
        # Notify listeners about decision
        for l in self._listeners:
            executed_order = OrderExecuted(side, assets_delta, suggested_price)
            l(executed_order)
    
    # remove listener will be implemented later on, when required
    def add_listener(self, listener: Callable[[OrderExecuted], None]):
        self._listeners.append(listener)

