from typing import cast
from avrogen.dict_wrapper import DictWrapper
from .schema_classes import _SCHEMA as get_schema_type
from .schema_classes import _json_converter as json_converter
from .schema_classes import OrderClass
from .schema_classes import OrderKindClass
from avro.io import DatumReader


class SpecificDatumReader(DatumReader):
    SCHEMA_TYPES = {
        "Order": OrderClass,
        ".Order": OrderClass,
        "onlexnet.ptn.signals.events.Order": OrderClass,
        "OrderKind": OrderKindClass,
        ".OrderKind": OrderKindClass,
        "onlexnet.ptn.signals.events.OrderKind": OrderKindClass,
    }
    
    
    def __init__(self, readers_schema=None, **kwargs):
        writers_schema = kwargs.pop("writers_schema", readers_schema)
        writers_schema = kwargs.pop("writer_schema", writers_schema)
        super(SpecificDatumReader, self).__init__(writers_schema, readers_schema, **kwargs)
    
    
    def read_record(self, writers_schema, readers_schema, decoder):
        result = super(SpecificDatumReader, self).read_record(writers_schema, readers_schema, decoder)
        
        if readers_schema.fullname in SpecificDatumReader.SCHEMA_TYPES:
            tp = SpecificDatumReader.SCHEMA_TYPES[readers_schema.fullname]
            if issubclass(tp, DictWrapper):
                result = tp._construct(result)
            else:
                # tp is an enum
                result = tp(result)  # type: ignore
        
        return result