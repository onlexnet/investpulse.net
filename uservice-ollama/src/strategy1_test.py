from datetime import date
import unittest

from numpy import datetime64
import numpy

from .YahooFinance import YahooFinanceData, YahooFinanceLoader
from .strategy1 import ComputeStrategy1, ComputeStrategyState, Decisions, SkipDecision

class ComputeStrategy1Test(unittest.TestCase):

    def test_should_calculate_result(self):
        state = ComputeStrategyState(budget=100, volume=10)
        loader = YahooFinanceLoader('MSFT')
        facts = loader.load_data(date.today())
        sut = ComputeStrategy1(facts, initial_state=state)
        fact = YahooFinanceData(datetime64('2020-01-01'), 1, 1, 1, 1, 1, 1)
        decision = sut.apply(fact)
        assert decision == SkipDecision()
