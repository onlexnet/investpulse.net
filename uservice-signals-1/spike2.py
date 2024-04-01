import onlexnet.dapr as d
import scheduler_rpc.onlexnet.ptn.scheduler.test.events as scheduler_test
import json
from src.logger import log
import os
from typing import Optional, cast
from dapr.clients.grpc._response import TopicEventResponse

from cloudevents.sdk.event import v1
from dapr.ext.grpc import App

from dapr.clients import DaprClient
import onlexnet.dapr as d
import market_rpc.onlexnet.pdt.market.events as market_events
import market_rpc
# the queue is thread safe

import src.data as data
from src.market import Publisher
import src.market as market

as_json = '{"adjClose":31.23305892944336,"close":37.15999984741211,"date":20140102,"high":37.400001525878906,"low":37.09999847412109,"open":37.34999847412109,"volume":30632200}'
as_dict = json.loads(as_json)
assert isinstance(as_dict, dict)

# reader = market_rpc.json_converter
# event_typed1: market_events.MarketChangedEvent = reader.from_json_object(as_dict)


event_typed = market_events.MarketChangedEvent._construct(as_dict)
assert isinstance(event_typed, market_events.MarketChangedEvent)
