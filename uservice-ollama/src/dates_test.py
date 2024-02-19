from cgi import test
from datetime import date

from .YahooFinance import LoadContext, load
from .dates import split

date_from = date(2019, 1, 1)
date_to = date(2023, 12, 31)
asset_name = 'MSFT'
load_context = LoadContext(date_from, date_to, asset_name)

def test_dates():
    data = load(load_context)
    split_result = split(data)
    initial_set = split_result.initial_set
    test_set = split_result.test_set
    initial_set_size = len(initial_set.index)
    assert initial_set_size in (251, 252, 253), "initial set size should cover 1 year (about 251 working days)"
    assert len(test_set.index) > 0, "Test set should contain some data"