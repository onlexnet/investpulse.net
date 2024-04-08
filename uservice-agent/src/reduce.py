import dataclasses
from functools import singledispatch
from typing import Callable
from .models import BuyOrder, ChangeBudget, MyState

def apply_budget(state: MyState, order: ChangeBudget) -> MyState:
    aaa = _apply_budget_ChangeBudget

def _apply_budget_ChangeBudget(state: MyState, order: ChangeBudget) -> MyState:
    new_budget = state.budget + order.delta
    result = dataclasses.replace(state, budget = new_budget )
    return result

def _apply_budget_float(state: MyState, order: BuyOrder) -> MyState:
    new_budget = state.budget + order.delta
    result = dataclasses.replace(state, budget = new_budget )
    return result

type handler[T] = Callable[[MyState, T], MyState]
