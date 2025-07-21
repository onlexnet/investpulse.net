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
    
    RECORD_SCHEMA = get_schema_type("onlexnet.market.events.MarketChangedEvent")
    def __init__(self,
        date: int,
    ):
        super().__init__()
        
        self.date = date
    
    def _restore_defaults(self) -> None:
        self.date = int()
    
    
    @property
    def date(self) -> int:
        # No docs available.
        return self._inner_dict.get('date')  # type: ignore
    
    @date.setter
    def date(self, value: int) -> None:
        self._inner_dict['date'] = value
    
    
__SCHEMA_TYPES = {
    'onlexnet.market.events.MarketChangedEvent': MarketChangedEventClass,
    'MarketChangedEvent': MarketChangedEventClass,
}

_json_converter = avrojson.AvroJsonConverter(use_logical_types=False, schema_types=__SCHEMA_TYPES)
avrojson.set_global_json_converter(_json_converter)

