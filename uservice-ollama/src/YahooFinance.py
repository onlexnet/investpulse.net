from strictly_typed_pandas import DataSet
import yfinance as yf
from datetime import date
import os
from attr import dataclass
from numpy import datetime64
from pandas import DataFrame
from sklearn.utils import assert_all_finite
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
    
class YahooFinanceLoader:
    def __init__(self, asset_name: str):
        self.asset_name = asset_name.upper()
        self.data = self.load_data(date.today())
        
    def load_data(self, end_date: date):
        start_date: date = date(2019, 1, 1) # 5+ years
        
        asset_folder = os.path.join('data_cache', self.asset_name.lower())
        os.makedirs(asset_folder, exist_ok=True)  # create folder, if exists

        file_name = f"{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}.csv"
        file_path = os.path.join(asset_folder, file_name)
        data_pd: DataFrame
        if not os.path.exists(file_path):
            data_yf = yf.download(self.asset_name, start=start_date, end=end_date)
            data_yf.to_csv(file_path)
        
        # read data and adjust column names to field names
        data_pd = pd.read_csv(file_path)
        data_pd = data_pd.rename(columns=lambda x: x.lower().replace(' ', '_'))
        # and adjust types
        data_pd['date'] = data_pd['date'].apply(pd.to_datetime)

        data = DataSet[YahooFinanceData](data_pd)
        return data