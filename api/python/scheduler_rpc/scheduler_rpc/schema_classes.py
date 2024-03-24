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

class BalanceReportRequestedEventClass(DictWrapper):
    # No docs available.
    
    RECORD_SCHEMA = get_schema_type("onlexnet.ptn.scheduler.events.BalanceReportRequestedEvent")
    def __init__(self,
    ):
        super().__init__()
        
    
    def _restore_defaults(self) -> None:
        pass
    
    
class NewTimeClass(DictWrapper):
    # No docs available.
    
    RECORD_SCHEMA = get_schema_type("onlexnet.ptn.scheduler.events.NewTime")
    def __init__(self,
        correlationId: str,
        yyyymmdd: int,
        hhmm: int,
    ):
        super().__init__()
        
        self.correlationId = correlationId
        self.yyyymmdd = yyyymmdd
        self.hhmm = hhmm
    
    def _restore_defaults(self) -> None:
        self.correlationId = str()
        self.yyyymmdd = int()
        self.hhmm = int()
    
    
    @property
    def correlationId(self) -> str:
        # No docs available.
        return self._inner_dict.get('correlationId')  # type: ignore
    
    @correlationId.setter
    def correlationId(self, value: str) -> None:
        self._inner_dict['correlationId'] = value
    
    
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
    
    
class NewTimeAppliedClass(DictWrapper):
    # No docs available.
    
    RECORD_SCHEMA = get_schema_type("onlexnet.ptn.scheduler.events.NewTimeApplied")
    def __init__(self,
        correlationId: str,
    ):
        super().__init__()
        
        self.correlationId = correlationId
    
    def _restore_defaults(self) -> None:
        self.correlationId = str()
    
    
    @property
    def correlationId(self) -> str:
        # No docs available.
        return self._inner_dict.get('correlationId')  # type: ignore
    
    @correlationId.setter
    def correlationId(self, value: str) -> None:
        self._inner_dict['correlationId'] = value
    
    
__SCHEMA_TYPES = {
    'onlexnet.ptn.scheduler.events.BalanceReportRequestedEvent': BalanceReportRequestedEventClass,
    'onlexnet.ptn.scheduler.events.NewTime': NewTimeClass,
    'onlexnet.ptn.scheduler.events.NewTimeApplied': NewTimeAppliedClass,
    'BalanceReportRequestedEvent': BalanceReportRequestedEventClass,
    'NewTime': NewTimeClass,
    'NewTimeApplied': NewTimeAppliedClass,
}

_json_converter = avrojson.AvroJsonConverter(use_logical_types=False, schema_types=__SCHEMA_TYPES)
avrojson.set_global_json_converter(_json_converter)

