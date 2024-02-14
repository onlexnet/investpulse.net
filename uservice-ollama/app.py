from dataclasses import dataclass
from typing import Any
from unicodedata import numeric
from numpy import datetime64, number
import numpy
from pandas import DataFrame, Timestamp
import pandas
from strictly_typed_pandas import DataSet
from typing import Callable
import yfinance as yf
from datetime import date, datetime
import os
import pandas as pd

class FinanceDataSchema:
    date: datetime64
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: int
    
class YahooFinanceData:
    def __init__(self, asset_name):
        self.asset_name = asset_name
        self.data = self.load_data(date.today())
        
    def load_data(self, end_date: date):
        start_date: date = date(2019, 1, 1) # 5+ years
        
        asset_folder = os.path.join('assets', self.asset_name)
        os.makedirs(asset_folder, exist_ok=True)  # create folder, if exists

        file_name = f"{ticker_symbol}_data_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}.csv"
        file_path = os.path.join(asset_folder, f'{file_name}.csv')
        data_pd: DataFrame
        if not os.path.exists(file_path):
            data_yf = yf.download(ticker_symbol, start=start_date, end=end_date)
            data_yf.to_csv(file_path)
        
        # read data and adjust column names to field names
        data_pd = pd.read_csv(file_path)
        data_pd = data_pd.rename(columns=lambda x: x.lower().replace(' ', '_'))
        # and adjust types
        data_pd['date'] = data_pd['date'].apply(pd.to_datetime)

        data = DataSet[FinanceDataSchema](data_pd)
        return data


# Define the ticker symbol
ticker_symbol = "MSFT"

def main():
    # Download the data or read from data cache
    msftData: YahooFinanceData = YahooFinanceData('MSFT')
    print (msftData.data)


if (__name__ == '__main__'):
    main()
