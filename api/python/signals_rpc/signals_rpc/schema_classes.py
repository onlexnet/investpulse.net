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
    
    RECORD_SCHEMA = get_schema_type("onlexnet.pdt.signals.events.Order")
    def __init__(self,
        kind: Union[str, "OrderKindClass"],
        wnen: "datetime6Class",
    ):
        super().__init__()
        
        self.kind = kind
        self.wnen = wnen
    
    def _restore_defaults(self) -> None:
        self.kind = OrderKindClass.BUY
        self.wnen = datetime6Class._construct_with_defaults()
    
    
    @property
    def kind(self) -> Union[str, "OrderKindClass"]:
        # No docs available.
        return self._inner_dict.get('kind')  # type: ignore
    
    @kind.setter
    def kind(self, value: Union[str, "OrderKindClass"]) -> None:
        self._inner_dict['kind'] = value
    
    
    @property
    def wnen(self) -> "datetime6Class":
        # No docs available.
        return self._inner_dict.get('wnen')  # type: ignore
    
    @wnen.setter
    def wnen(self, value: "datetime6Class") -> None:
        self._inner_dict['wnen'] = value
    
    
class OrderKindClass(object):
    # No docs available.
    
    BUY = "BUY"
    SELL = "SELL"
    
    
class datetime6Class(DictWrapper):
    # No docs available.
    
    RECORD_SCHEMA = get_schema_type("onlexnet.pdt.signals.events.datetime6")
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
    'onlexnet.pdt.signals.events.Order': OrderClass,
    'onlexnet.pdt.signals.events.OrderKind': OrderKindClass,
    'onlexnet.pdt.signals.events.datetime6': datetime6Class,
    'Order': OrderClass,
    'OrderKind': OrderKindClass,
    'datetime6': datetime6Class,
}

_json_converter = avrojson.AvroJsonConverter(use_logical_types=False, schema_types=__SCHEMA_TYPES)
avrojson.set_global_json_converter(_json_converter)

