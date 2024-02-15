import unittest
from .strategy1 import ComputeStrategy1

class ComputeStrategy1Test(unittest.TestCase):

    def test_should_calculate_result(self):
        sut = ComputeStrategy1(budget=100, initial_volume=10)
