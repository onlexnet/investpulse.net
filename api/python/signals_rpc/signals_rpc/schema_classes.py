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

class OrderClass(DictWrapper):
    # No docs available.
    
    RECORD_SCHEMA = get_schema_type("onlexnet.ptn.signals.events.Order")
    def __init__(self,
        kind: Union[str, "OrderKindClass"],
        amount: str,
        yyyymmdd: int,
        hhmm: int,
    ):
        super().__init__()
        
        self.kind = kind
        self.amount = amount
        self.yyyymmdd = yyyymmdd
        self.hhmm = hhmm
    
    def _restore_defaults(self) -> None:
        self.kind = OrderKindClass.BUY
        self.amount = str()
        self.yyyymmdd = int()
        self.hhmm = int()
    
    
    @property
    def kind(self) -> Union[str, "OrderKindClass"]:
        # No docs available.
        return self._inner_dict.get('kind')  # type: ignore
    
    @kind.setter
    def kind(self, value: Union[str, "OrderKindClass"]) -> None:
        self._inner_dict['kind'] = value
    
    
    @property
    def amount(self) -> str:
        """bbbbbbbbbbbbbb"""
        return self._inner_dict.get('amount')  # type: ignore
    
    @amount.setter
    def amount(self, value: str) -> None:
        self._inner_dict['amount'] = value
    
    
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
    
    
class OrderKindClass(object):
    # No docs available.
    
    BUY = "BUY"
    SELL = "SELL"
    
    
__SCHEMA_TYPES = {
    'onlexnet.ptn.signals.events.Order': OrderClass,
    'onlexnet.ptn.signals.events.OrderKind': OrderKindClass,
    'Order': OrderClass,
    'OrderKind': OrderKindClass,
}

_json_converter = avrojson.AvroJsonConverter(use_logical_types=False, schema_types=__SCHEMA_TYPES)
avrojson.set_global_json_converter(_json_converter)

