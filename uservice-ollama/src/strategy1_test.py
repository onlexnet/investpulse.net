import unittest

from numpy import datetime64
import numpy

from .YahooFinance import YahooFinanceData
from .strategy1 import ComputeStrategy1, Decisions, SkipDecision

class ComputeStrategy1Test(unittest.TestCase):

    def test_should_calculate_result(self):
        sut = ComputeStrategy1(budget=100, initial_volume=10)
        fact = YahooFinanceData(datetime64('2020-01-01'), 1, 1, 1, 1, 1, 1)
        decision = sut.apply(fact)
        assert decision == SkipDecision()
