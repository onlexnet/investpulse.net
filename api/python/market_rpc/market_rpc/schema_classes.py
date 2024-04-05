import json
import os.path
import decimal
import datetime
import six
from avrogen.dict_wrapper import DictWrapper
from avrogen import avrojson
from avro.schema import RecordSchema, make_avsc_object
from avro import schema as avro_schema
from typing import ClassVar, List, Dict, Union, Optional, Type


def __read_file(file_name):
    with open(file_name, "r") as f:
        return f.read()
        

def __get_names_and_schema(json_str):
    names = avro_schema.Names()
    schema = make_avsc_object(json.loads(json_str), names)
    return names, schema


_SCHEMA_JSON_STR = __read_file(os.path.join(os.path.dirname(__file__), "schema.avsc"))


__NAMES, _SCHEMA = __get_names_and_schema(_SCHEMA_JSON_STR)
__SCHEMAS: Dict[str, RecordSchema] = {}


def get_schema_type(fullname: str) -> RecordSchema:
    return __SCHEMAS[fullname]
    
    
__SCHEMAS = dict((n.fullname.lstrip("."), n) for n in six.itervalues(__NAMES.names))

class MarketChangedEventClass(DictWrapper):
    # No docs available.
    
    RECORD_SCHEMA = get_schema_type("onlexnet.pdt.market.events.MarketChangedEvent")
    def __init__(self,
        when: "datetime5Class",
        ticker: str,
        whenyyyymmddhhmm: int,
        date: int,
        open: float,
        high: float,
        low: float,
        close: float,
        adjClose: float,
        volume: int,
    ):
        super().__init__()
        
        self.when = when
        self.ticker = ticker
        self.whenyyyymmddhhmm = whenyyyymmddhhmm
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.adjClose = adjClose
        self.volume = volume
    
    def _restore_defaults(self) -> None:
        self.when = datetime5Class._construct_with_defaults()
        self.ticker = str()
        self.whenyyyymmddhhmm = int()
        self.date = int()
        self.open = float()
        self.high = float()
        self.low = float()
        self.close = float()
        self.adjClose = float()
        self.volume = int()
    
    
    @property
    def when(self) -> "datetime5Class":
        # No docs available.
        return self._inner_dict.get('when')  # type: ignore
    
    @when.setter
    def when(self, value: "datetime5Class") -> None:
        self._inner_dict['when'] = value
    
    
    @property
    def ticker(self) -> str:
        # No docs available.
        return self._inner_dict.get('ticker')  # type: ignore
    
    @ticker.setter
    def ticker(self, value: str) -> None:
        self._inner_dict['ticker'] = value
    
    
    @property
    def whenyyyymmddhhmm(self) -> int:
        # No docs available.
        return self._inner_dict.get('whenyyyymmddhhmm')  # type: ignore
    
    @whenyyyymmddhhmm.setter
    def whenyyyymmddhhmm(self, value: int) -> None:
        self._inner_dict['whenyyyymmddhhmm'] = value
    
    
    @property
    def date(self) -> int:
        # No docs available.
        return self._inner_dict.get('date')  # type: ignore
    
    @date.setter
    def date(self, value: int) -> None:
        self._inner_dict['date'] = value
    
    
    @property
    def open(self) -> float:
        # No docs available.
        return self._inner_dict.get('open')  # type: ignore
    
    @open.setter
    def open(self, value: float) -> None:
        self._inner_dict['open'] = value
    
    
    @property
    def high(self) -> float:
        # No docs available.
        return self._inner_dict.get('high')  # type: ignore
    
    @high.setter
    def high(self, value: float) -> None:
        self._inner_dict['high'] = value
    
    
    @property
    def low(self) -> float:
        # No docs available.
        return self._inner_dict.get('low')  # type: ignore
    
    @low.setter
    def low(self, value: float) -> None:
        self._inner_dict['low'] = value
    
    
    @property
    def close(self) -> float:
        # No docs available.
        return self._inner_dict.get('close')  # type: ignore
    
    @close.setter
    def close(self, value: float) -> None:
        self._inner_dict['close'] = value
    
    
    @property
    def adjClose(self) -> float:
        # No docs available.
        return self._inner_dict.get('adjClose')  # type: ignore
    
    @adjClose.setter
    def adjClose(self, value: float) -> None:
        self._inner_dict['adjClose'] = value
    
    
    @property
    def volume(self) -> int:
        # No docs available.
        return self._inner_dict.get('volume')  # type: ignore
    
    @volume.setter
    def volume(self, value: int) -> None:
        self._inner_dict['volume'] = value
    
    
class datetime5Class(DictWrapper):
    # No docs available.
    
    RECORD_SCHEMA = get_schema_type("onlexnet.pdt.market.events.datetime5")
    def __init__(self,
        yyyymmdd: int,
        hhmm: int,
    ):
        super().__init__()
        
        self.yyyymmdd = yyyymmdd
        self.hhmm = hhmm
    
    def _restore_defaults(self) -> None:
        self.yyyymmdd = int()
        self.hhmm = int()
    
    
    @property
    def yyyymmdd(self) -> int:
        # No docs available.
        return self._inner_dict.get('yyyymmdd')  # type: ignore
    
    @yyyymmdd.setter
    def yyyymmdd(self, value: int) -> None:
        self._inner_dict['yyyymmdd'] = value
    
    
    @property
    def hhmm(self) -> int:
        # No docs available.
        return self._inner_dict.get('hhmm')  # type: ignore
    
    @hhmm.setter
    def hhmm(self, value: int) -> None:
        self._inner_dict['hhmm'] = value
    
    
__SCHEMA_TYPES = {
    'onlexnet.pdt.market.events.MarketChangedEvent': MarketChangedEventClass,
    'onlexnet.pdt.market.events.datetime5': datetime5Class,
    'MarketChangedEvent': MarketChangedEventClass,
    'datetime5': datetime5Class,
}

_json_converter = avrojson.AvroJsonConverter(use_logical_types=False, schema_types=__SCHEMA_TYPES)
avrojson.set_global_json_converter(_json_converter)

