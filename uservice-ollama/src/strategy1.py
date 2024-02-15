# 1. Load data 
# 2. read date 0
# 2a. create initial portfolio
# 2b. Define initial budget to allocate assets
# 3. start operations loop on date 1 year
# 4. create ML for the pass
# 5. Calculate portfolio value
# 6. Predict price next day for open, close
# 7. Measure risks
# 8. Decide to buy / decide to sell (if any asset in portfolio)
# 9. Bulid stats
# 10. Continue till the last date
# 11. Present results

from dataclasses import dataclass
from strictly_typed_pandas import DataSet

from .YahooFinance import YahooFinanceData

@dataclass
class Result:
    profit: int
    loss: int
        
    
class ComputeStrategy1:
    
    def __init__(self, budget: float, initial_volume: int):
        initial_portfolio = 2 # I have two MSFT assets
        
    def apply(self, item: YahooFinanceData) -> Result:
        return Result(0, 0)

    