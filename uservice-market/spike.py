from typing import cast
from avro.io import BinaryEncoder
import io
import asyncio
from io import BytesIO
import io
import time

from market_rpc.onlexnet.pdt.market.events import MarketChangedEvent
import fastavro




new_schema = {
    "type": "record",
    "name": "test_schema_migration_writer_union_new",
    "fields": [{
        "name": "test",
        "type": "int"
    }]
}

new_file = BytesIO()
record = {"test": 1}
buffer = io.BytesIO()
fastavro.schemaless_writer(new_file, new_schema, record)
new_file.seek(0)
buff = new_file.read()
new_file.seek(0)
new_reader = fastavro.schemaless_reader(new_file, new_schema)



event = MarketChangedEvent(20010203)
event_as_dict = event.to_obj()
fo = BytesIO()
schema = MarketChangedEvent.RECORD_SCHEMA.to_json()
fastavro.schemaless_writer(fo, schema, event_as_dict)
fo.seek(0)
bytes = fo.read()
print(len(bytes))

fo.seek(0)
aaa: MarketChangedEvent = cast(MarketChangedEvent, fastavro.schemaless_reader(fo, schema))

fo1 = BytesIO(b"some initial binary data: \x00\x01")
print(len(fo1.read()))
print(len(fo1.read()))
# assert len(bytes) == 14
