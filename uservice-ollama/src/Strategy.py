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
import dataclasses
from datetime import date
from sre_parse import State
import pandas
from pandas import DataFrame
from pandas import Series
from strictly_typed_pandas import DataSet
from ta.trend import MACD

from .MarketAgent import OrderExecuted, MarketAgent, Side

from .YahooFinance import YahooFinanceData

@dataclass
class ComputeStrategyState:
    # Money allowed to be spent on BuyDecision, returned by SellDecision
    volume: int = 0
    
class ComputeStrategy1:
    state: ComputeStrategyState
    
    def __init__(self, facts: DataSet[YahooFinanceData], initial_state: ComputeStrategyState, agent: MarketAgent):
        self.facts = facts
        self.state = initial_state
        self.agent = agent
        def listener(event: OrderExecuted) -> None:
            self.state.volume += event.amount
        agent.add_listener(listener)
    
    # data represents latest day, and we have to provide decision about
    # what     
    def apply(self, fact: YahooFinanceData) -> None:
        fact_as_dict = dataclasses.asdict(fact)
        fact_as_dataframe = DataFrame([fact_as_dict])
        df = pandas.concat([self.facts, fact_as_dataframe], ignore_index=True)
        macd = MACD(df['close'],window_fast=12, window_slow=26, window_sign=9)
        df['macd'] = macd.macd()
        df['signal_line'] = macd.macd_signal()
        # Suggest buying when the MACD value crosses above the signal line, and selling when it falls below the signal line.
        df['buy_signal'] = (df['macd'] > df['signal_line']) & (df['macd'].shift(1) < df['signal_line'].shift(1))
        self.facts = df

        last_row = df.iloc[-1]
        buy_signal = last_row['buy_signal']
        print("SPARTA")
        print(buy_signal)
        if buy_signal:
            d = pandas.to_datetime(fact.date)
            self.agent.make_order(Side.BUY, 1, d)
    
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

    