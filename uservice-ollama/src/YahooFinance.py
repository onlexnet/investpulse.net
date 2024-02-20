from dataclasses import dataclass
from strictly_typed_pandas import DataSet
import yfinance as yf
from datetime import date
import os
from numpy import datetime64
from pandas import DataFrame
import pandas as pd

@dataclass
class YahooFinanceData:
    date: datetime64
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: int

@dataclass
class LoadContext:
    date_from: date
    date_to: date
    # e.g. MSFT
    asset_name: str

def load(ctx: LoadContext) -> DataSet[YahooFinanceData]:
    start_date = ctx.date_from
    asset_name = ctx.asset_name
    end_date = ctx.date_to
    
    asset_folder = os.path.join('data_cache', asset_name.lower())
    os.makedirs(asset_folder, exist_ok=True)  # create folder, if exists

    file_name = f"{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}.csv"
    file_path = os.path.join(asset_folder, file_name)
    data_pd: DataFrame
    if not os.path.exists(file_path):
        data_yf = yf.download(asset_name, start=start_date, end=end_date)
        data_yf.to_csv(file_path)
        
    # read data and adjust column names to field names
    data_pd = pd.read_csv(file_path)
    data_pd = data_pd.rename(columns=lambda x: x.lower().replace(' ', '_'))
    # and adjust types
    # to_numpy: Callable[Timestamp (self) -> np.datetime64
    data_pd['date'] = data_pd['date'].apply(pd.to_datetime, format='ISO8601')
        
    data = DataSet[YahooFinanceData](data_pd)
    return data