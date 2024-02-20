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

    def test_should_calculate_result(self):
        agent = MarketAgent()
        state = ComputeStrategyState(volume=0)
        facts = DataSet[YahooFinanceData]()
        sut = ComputeStrategy1(facts, state, agent)
        fact = YahooFinanceData(datetime64('2020-01-01'), 1, 1, 1, 1, 1, 1)
        sut.apply(fact)
        
        assert state.volume == 1

    def skip_test_should_buy(self):
        agent = MarketAgent()
        state = ComputeStrategyState(volume=0)
        
        load_context = dates_test.msft_context
        yahoo_data = load(load_context)
        
        facts = DataSet[YahooFinanceData]()
        sut = ComputeStrategy1(facts, state, agent)
        fact = YahooFinanceData(datetime64('2020-01-01'), 1, 1, 1, 1, 1, 1)
        sut.apply(fact)
