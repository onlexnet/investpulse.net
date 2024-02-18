from dataclasses import dataclass
from typing import Any
from unicodedata import numeric
from numpy import datetime64
import numpy
from pandas import DataFrame
from strictly_typed_pandas import DataSet
from datetime import date, datetime
import os

import YahooFinance


# Define the ticker symbol
ticker_symbol = "MSFT"

def main():
    # Download the data or read from data cache
    msftData: YahooFinance = YahooFinance('MSFT')
    print (msftData.data)


if (__name__ == '__main__'):
    main()
