from dataclasses import dataclass, field


@dataclass(frozen=True)
class MyState:
  budget: float = 0
  owned: dict[str, int] = field(default_factory=dict)

@dataclass(frozen=True)
class ChangeBudget:
  delta: float

@dataclass(frozen=True)
class BuyOrder:
  """Ticker"""
  ticker: str
  """Price which should be used to by the asset"""
  price: float
