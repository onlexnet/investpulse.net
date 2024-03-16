from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class MarketChangedEventProtoExample(_message.Message):
    __slots__ = ("date", "open", "close", "low", "high", "adj_close")
    DATE_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    ADJ_CLOSE_FIELD_NUMBER: _ClassVar[int]
    date: int
    open: float
    close: float
    low: float
    high: float
    adj_close: float
    def __init__(self, date: _Optional[int] = ..., open: _Optional[float] = ..., close: _Optional[float] = ..., low: _Optional[float] = ..., high: _Optional[float] = ..., adj_close: _Optional[float] = ...) -> None: ...
