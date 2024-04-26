from datetime import datetime
from onlexnet.convert import from_datetime5, to_datetime5


def test_datetime5():

    assert from_datetime5(200102030405) == datetime(2001, 2, 3, 4, 5)

    assert to_datetime5(datetime(2001, 2, 3, 4, 5)) == 200102030405