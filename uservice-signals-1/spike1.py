import onlexnet.dapr as d
import scheduler_rpc.onlexnet.ptn.scheduler.test.events as scheduler_test
import json
import logging
import os
import threading
from typing import Optional, cast
from dapr.clients.grpc._response import TopicEventResponse

from cloudevents.sdk.event import v1
from dapr.ext.grpc import App

from dapr.clients import DaprClient
import scheduler_rpc.onlexnet.ptn.scheduler.events as events
import onlexnet.dapr as d
import pandas as pd
import market_rpc.onlexnet.pdt.market.events as market_events
# the queue is thread safe
from queue import Queue

APP_PORT=os.getenv('APP_PORT')

app = App()

log = logging.getLogger(__name__)
log.setLevel(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()  # Log to the console
handler.setFormatter(formatter)
log.addHandler(handler)
log.info("aaaaaaaaaaaaa")