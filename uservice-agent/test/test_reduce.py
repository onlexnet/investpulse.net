from unittest import TestCase

from src.reduce import apply_budget
from src.models import BuyOrder, ChangeBudget, MyState



class TestReduce(TestCase):

    def test_apply_reduce_1(self):

        given = MyState(budget=1)

        actual = apply_budget(given, ChangeBudget(2))

        expected = MyState(budget=3)
        self.assertEqual(actual, expected)

    def test_apply_reduce_2(self):

        given = MyState(budget=3)

        actual = apply_budget(given, BuyOrder("msft", 1))

        expected = MyState(budget=0, owned={ "msft": 3 })
        self.assertEqual(actual, expected)
