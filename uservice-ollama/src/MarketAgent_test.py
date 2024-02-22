from datetime import date
from typing import Optional
import unittest

from .MarketAgent import AmountOptions, OrderExecuted, MarketAgent, Side


class MarketAgentTest(unittest.TestCase):
    
    def test_should_buy_assets_as_possible_by_budget(self):

        amount: int = 0
        
        budget = 1_000
        sut = MarketAgent(budget, { })
        def my_listener(event: OrderExecuted):
            nonlocal amount
            amount = event.amount
            
        sut.add_listener(my_listener)

        suggested_price = 100
        sut.make_order(Side.BUY, AmountOptions.MAX, date(2000, 1, 1), suggested_price)

        expected_amount = 10
        assert amount == expected_amount, f"budget: {budget}, asset price: {suggested_price}, so we expect {expected_amount} assets"

    def test_should_sell_assets_as_possible(self):

        initial_budget = 1_000
        controlled_assets_msft = 3
        
        actual_assets = controlled_assets_msft
        sut = MarketAgent(initial_budget, {'msft': actual_assets})
        def my_listener(event: OrderExecuted):
            nonlocal actual_assets
            amount_delta = event.amount if event.side == Side.BUY else -event.amount
            actual_assets += amount_delta
            
        sut.add_listener(my_listener)

        suggested_price = 100
        sut.make_order(Side.SELL, AmountOptions.MAX, date(2000, 1, 1), suggested_price)

        expected_amount = 0
        expected_budget = initial_budget + suggested_price * controlled_assets_msft
        assert actual_assets == expected_amount
        assert sut._budget == expected_budget

    def test_should_sell_assets_partially(self):

        controlled_assets_msft = 3 # more than one as we are going to sell 1 asset
        
        order_executed: Optional[OrderExecuted] = None
        sut = MarketAgent(controlled_assets = {'msft': controlled_assets_msft})
        def my_listener(event: OrderExecuted):
            nonlocal order_executed
            order_executed = event
            
        sut.add_listener(my_listener)

        suggested_price = 100
        sut.make_order(Side.SELL, 1, date(2000, 1, 1), suggested_price)

        assert order_executed == OrderExecuted(Side.SELL, 1, 100)

    def test_should_buy_and_sell(self):

        order_executed: Optional[OrderExecuted] = None
        initial_budget = 1000
        sut = MarketAgent(budget=initial_budget)
            
        suggested_price = 100
        sut.make_order(Side.BUY, 1, date(2000, 1, 1), suggested_price)
        sut.make_order(Side.BUY, 1, date(2000, 1, 1), suggested_price)
        assert sut._budget == initial_budget - 2 * suggested_price

        sut.make_order(Side.SELL, AmountOptions.MAX, date(2000, 1, 1), suggested_price)
        assert sut._budget == initial_budget
        assert sut._assets['msft'] == 0

