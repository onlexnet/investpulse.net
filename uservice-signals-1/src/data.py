from enum import Enum
from threading import Lock
from typing import Any
import pandas as pd
import market_rpc.onlexnet.pdt.market.events as market_events
from ta.trend import MACD

from src.logger import log


df = pd.DataFrame({'date': [], 'open': [],'close': [], 'adj_close': []})
lock = Lock()

class ORDER(Enum):
    NONE = 0,
    BUY = 1,
    SELL = 2

def add_event(event: market_events.MarketChangedEvent) -> ORDER:
    date = event.date
    with lock:
        row = df.loc[df['date'] == date]
        if row.empty:
            last_index = len(df)
            as_dict: Any = event._inner_dict
            df.loc[last_index] = as_dict
    
        macd = MACD(df['close'], window_fast=12, window_slow=26, window_sign=9)
        df['macd'] = macd.macd()
        df['signal_line'] = macd.macd_signal()
        # Suggest buying when the MACD value crosses above the signal line, and selling when it falls below the signal line.
        df['buy_signal'] = (df['macd'] > df['signal_line']) & (df['macd'].shift(1) < df['signal_line'].shift(1))
        df['sell_signal'] = (df['macd'] < df['signal_line']) & (df['macd'].shift(1) > df['signal_line'].shift(1))

        last_row = df.iloc[-1]
        buy_signal = last_row['buy_signal']
        sell_signal = last_row['sell_signal']

        d = pd.to_datetime(date)
        if buy_signal:
            return ORDER.BUY
        if sell_signal:
            return ORDER.SELL
        return ORDER.NONE

