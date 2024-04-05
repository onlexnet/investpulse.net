from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BuyOrder(_message.Message):
    __slots__ = ("clientId", "ticker", "amount")
    CLIENTID_FIELD_NUMBER: _ClassVar[int]
    TICKER_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    clientId: str
    ticker: str
    amount: float
    def __init__(self, clientId: _Optional[str] = ..., ticker: _Optional[str] = ..., amount: _Optional[float] = ...) -> None: ...

class SellOrder(_message.Message):
    __slots__ = ("clientId", "ticker", "amount")
    CLIENTID_FIELD_NUMBER: _ClassVar[int]
    TICKER_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    clientId: str
    ticker: str
    amount: float
    def __init__(self, clientId: _Optional[str] = ..., ticker: _Optional[str] = ..., amount: _Optional[float] = ...) -> None: ...

class OrderBook(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Finished(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class State(_message.Message):
    __slots__ = ("orderBook", "finished", "budget")
    ORDERBOOK_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    BUDGET_FIELD_NUMBER: _ClassVar[int]
    orderBook: OrderBook
    finished: Finished
    budget: float
    def __init__(self, orderBook: _Optional[_Union[OrderBook, _Mapping]] = ..., finished: _Optional[_Union[Finished, _Mapping]] = ..., budget: _Optional[float] = ...) -> None: ...
