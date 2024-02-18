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
from sre_parse import State
from strictly_typed_pandas import DataSet

from .YahooFinance import YahooFinanceData

@dataclass
class BuyDecision:
    volumen: int
    price: float

@dataclass
class SellDecision:
    volumen: int
    price: float
    
@dataclass
class SkipDecision:
    pass

Decisions = BuyDecision | SellDecision | SkipDecision
        
@dataclass
class ComputeStrategyState:
    # Money allowed to be spent on BuyDecision, returned by SellDecision
    budget: float
    volume: int = 0
    
class ComputeStrategy1:
    state: ComputeStrategyState
    
    def __init__(self, facts: DataSet[YahooFinanceData], initial_state: ComputeStrategyState):
        self.state = initial_state
        
        assert len(facts) in (260, 261, 262)
        
    # data represents latest day, and we have to provide decision about
    # what     
    def apply(self, fact: YahooFinanceData) -> Decisions:

        return SkipDecision()
    
# https://chat.openai.com/c/49e12137-0be2-4189-915c-3bea686abfe5
# import pandas as pd
# from ta.trend import MACD
# import matplotlib.pyplot as plt

# Załaduj dane z pliku CSV (data.csv)
# df = pd.read_csv('data.csv')

# # Oblicz wskaźniki techniczne, w tym MACD
# df['macd'] = MACD(df['Close']).macd()
# df['signal_line'] = MACD(df['Close']).macd_signal()

# # Sugeruj kupno, gdy wartość MACD przekracza linię sygnałową, i sprzedaż, gdy spada poniżej lini sygnałowej
# df['buy_signal'] = df['macd'] > df['signal_line']
# df['sell_signal'] = df['macd'] < df['signal_line']

# # Wykres z ceną akcji, MACD i sygnałami kupna/sprzedaży
# plt.figure(figsize=(12,6))
# plt.plot(df['Close'], label='Close Price', color='blue')
# plt.scatter(df.index[df['buy_signal']], df['Close'][df['buy_signal']], marker='^', color='green', label='Buy Signal')
# plt.scatter(df.index[df['sell_signal']], df['Close'][df['sell_signal']], marker='v', color='red', label='Sell Signal')
# plt.legend()
# plt.title('Price with MACD Buy/Sell Signals')
# plt.xlabel('Date')
# plt.ylabel('Price')
# plt.show()

    