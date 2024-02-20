from dataclasses import dataclass
import dataclasses
from datetime import date
import unittest

from numpy import datetime64
import numpy
from strictly_typed_pandas import DataSet

from .MarketAgent import MarketAgent

from . import dates
from . import dates_test

from .YahooFinance import LoadContext, YahooFinanceData, load
from .Strategy import ComputeStrategy1, ComputeStrategyState

class ComputeStrategy1Test(unittest.TestCase):

    def _skip_test_should_calculate_result(self):
        agent = MarketAgent()
        state = ComputeStrategyState(volume=0)
        facts = DataSet[YahooFinanceData]()
        sut = ComputeStrategy1(facts, state, agent)
        fact = YahooFinanceData(datetime64('2020-01-01'), 1, 1, 1, 1, 1, 1)
        sut.apply(fact)
        
        assert state.volume == 1

    def test_should_buy(self):
        """
        To generate a "buy" signal, we need the MACD line to cross above the signal line. 
        Let's consider input data:
        Day 1: 10
        Day 2: 9
        Day 3: 8
        Day 4: 10
        Day 5: 12
        Day 6: 14
        Day 7: 16
        We'll use MACD periods of 12, 26, and 9 days.
        After calculating the MACD and the MACD signal line for each day, we observe where the MACD line crosses above the signal line.
        This intersection point is a potential "buy" signal. In this case, for the provided data, the crossing point could be on Day 5
        or Day 6, indicating a potential "buy" signal.
        """
        agent = MarketAgent()
        state = ComputeStrategyState(volume=0)
        
        load_context = dates_test.msft_context
        yahoo_data = load(load_context)
        
        facts = DataSet[YahooFinanceData]()
        sut = ComputeStrategy1(facts, state, agent)

        close = [
    100.0, 101.5, 102.2, 103.1, 102.8, 102.0, 101.2, 100.5, 100.0, 99.7,
    99.2, 98.9, 99.4, 100.1, 101.0, 101.8, 102.3, 103.0, 103.5, 104.2,
    104.8, 105.3, 105.1, 104.7, 104.2, 103.5, 102.8, 102.0, 101.3, 100.5,
    100.0, 99.5, 99.0, 98.7, 99.2, 99.9, 100.6, 101.2, 101.9, 102.5,
    103.0, 103.4, 103.9, 104.3, 104.6, 104.9, 105.1, 104.8, 104.4, 103.9,
    103.3, 102.6, 101.9, 101.2, 100.5, 100.0, 99.5, 99.0, 98.7, 99.2, 99.9,
    100.6, 101.2, 101.9, 102.5, 103.0, 103.4, 103.9, 104.3, 104.6, 104.9,
    105.1, 104.8, 104.4, 103.9, 103.3, 102.6, 101.9, 101.2, 100.5, 100.0,
]
        # prices = [95, 100, 105, 110, 115]
        now = datetime64('1999-12-31')
        for idx, x in enumerate(close):
            date = now + numpy.timedelta64(idx, 'D')
            data = YahooFinanceData(date, 0, 0, 0, x, 0, 0)
            sut.apply(data)
            sut.apply

        assert state.volume == 2
