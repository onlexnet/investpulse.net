import dataclasses
from typing import Callable
from .models import BuyOrder, ChangeBudget, MyState

type OrderType = ChangeBudget | BuyOrder

def apply_budget(state: MyState, order: OrderType) -> MyState:
  if isinstance(order, ChangeBudget):
    return _apply_budget_ChangeBudget(state, order)
  elif isinstance(order, BuyOrder):
    return _apply_budget_BuyOrder(state, order)
  else:
     raise ValueError(f'Illegal OrderType: {order}')

def _apply_budget_ChangeBudget(state: MyState, order: ChangeBudget) -> MyState:
    new_budget = state.budget + order.delta
    result = dataclasses.replace(state, budget = new_budget )
    return result

def _apply_budget_BuyOrder(state: MyState, order: BuyOrder) -> MyState:
    items_to_buy = int(state.budget // order.price)
    total_amount = items_to_buy * order.price
    new_budget = state.budget - total_amount
    owned = state.owned.copy()
    ticker = order.ticker
    items = owned.get(ticker) or 0
    items_after_order = items + items_to_buy
    owned[ticker] = items_after_order
    result = dataclasses.replace(state, budget = new_budget,  )
    return result

