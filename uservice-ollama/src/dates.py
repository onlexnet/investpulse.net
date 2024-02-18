from dataclasses import dataclass
import numpy
import pandas

from strictly_typed_pandas import DataSet
from .YahooFinance import YahooFinanceData

@dataclass
class SplitResult:
    # Initial set (1 year) is required to observe full cycle of data
    initial_set: DataSet[YahooFinanceData]
    test_set: DataSet[YahooFinanceData]
    
def split(data: DataSet[YahooFinanceData]) -> SplitResult:
    initial_row: YahooFinanceData = data.loc[data.index[0]]
    initial_date = initial_row.date
    next_year = initial_date + numpy.timedelta64(365,'D')
    
    df1 = DataSet(data[data['date'] < next_year])
    df2 = DataSet(data[data['date'] >= next_year])
    return SplitResult(df1, df2)