from datetime import date
import unittest

from .MarketAgent import OrderExecuted, MarketAgent, Side


class MarketAgentTest(unittest.TestCase):
    
    def test_should_buy(self):
        sut = MarketAgent()
        
        x11: int = 42
        x22: date
        
        def my_listener(a: OrderExecuted):
            nonlocal x11
            x11 = a.amount
            
        sut.add_listener(my_listener)
        sut.make_order(Side.BUY, 1, date(2000, 1, 1))

        assert x11 == 1
