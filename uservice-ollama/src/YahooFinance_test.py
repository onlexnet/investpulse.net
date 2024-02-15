import unittest

from .YahooFinance import YahooFinanceLoader


class YahooFinanceDataTest(unittest.TestCase):
    
    def test_should_load_example_data(self):
        sut = YahooFinanceLoader('MSFT')
