from datetime import date
import unittest

from numpy import datetime64
import numpy
from strictly_typed_pandas import DataSet

from . import dates
from . import dates_test

from .YahooFinance import LoadContext, YahooFinanceData, load
from .strategy1 import ComputeStrategy1, ComputeStrategyState, Decisions, SkipDecision

class ComputeStrategy1Test(unittest.TestCase):

    def test_should_calculate_result(self):
        state = ComputeStrategyState(budget=100, volume=10)
        load_context = dates_test.load_context
        yahoo_data = load(load_context)
        facts = DataSet[YahooFinanceData]()
        sut = ComputeStrategy1(facts, initial_state=state)
        fact = YahooFinanceData(datetime64('2020-01-01'), 1, 1, 1, 1, 1, 1)
        decision = sut.apply(fact)
        assert decision == SkipDecision()
