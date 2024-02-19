import unittest

from .YahooFinance import load

from . import dates_test
from . import dates

def test_should_load_example_data():
    load_ctx = dates_test.load_context
    load(load_ctx)
