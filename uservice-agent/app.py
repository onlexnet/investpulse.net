import asyncio
from concurrent import futures
from datetime import date, timedelta
import datetime
from io import BytesIO
import json
import logging
import os
from typing import Optional, cast
from venv import logger
from dapr.clients.grpc._response import TopicEventResponse

from cloudevents.sdk.event import v1
from dapr.ext.grpc import App

from dapr.clients import DaprClient
from dapr.aio.clients import DaprClient as DaprClientAsync
from avro import datafile, io
import scheduler_rpc.onlexnet.ptn.scheduler.events as events
import market_rpc.onlexnet.pdt.market.events as me
import onlexnet.dapr as d
import pandas as pd
from threading import Lock
from agent_rpc.schema_pb2_grpc import AgentServicer, add_AgentServicer_to_server, Agent
from agent_rpc.schema_pb2 import State, OrderBook, Finished

APP_PORT=int(os.getenv('APP_PORT', 50000))
log = logging.getLogger("myapp")

app = App()

class MyService(AgentServicer):
    def __init__(self, dapr: DaprClient) -> None:
        self.dapr = dapr

    def buy(self, request, context):
        log.info("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        log.info(request)
        return State(orderBook=OrderBook(), finished=Finished(), budget=2000)

    def sell(self, request, context):
        log.info("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
        return State(orderBook=OrderBook(), finished=Finished(), budget=2000)


@app.subscribe(pubsub_name='pubsub', topic=d.as_topic_name(events.BalanceReportRequestedEvent))
def on_BalanceReportRequestedEvent(event: v1.Event) -> Optional[TopicEventResponse]:
    # Returning None (or not doing a return explicitly) is equivalent
    # to returning a TopicEventResponse("success").
    # You can also return TopicEventResponse("retry") for dapr to log
    # the message and retry delivery later, or TopicEventResponse("drop")
    # for it to drop the message

    # store financial result raport as requested by the event

    # list of name, degree, score
    nme = ["aparna", "pankaj", "sudhir", "Geeku"]
    deg = ["MBA", "BCA", "M.Tech", "MBA"]
    scr = [90, 40, 80, 98]

    # dictionary of lists
    dict = {'name': nme, 'degree': deg, 'score': scr}

    df = pd.DataFrame(dict)
    asset_name = "test"
    asset_folder = os.path.join('.reports', asset_name.lower())
    os.makedirs(asset_folder, exist_ok=True)  # create folder, if exists
    start_date = datetime.datetime.now()
    file_name = f"{start_date.strftime('%Y-%m-%d')}.csv"
    file_path = os.path.join(asset_folder, file_name)
    df.to_csv(file_path)


    df.to_csv()

    return TopicEventResponse("success")

lock = Lock()
market: dict[str, me.MarketChangedEvent] = {}

async def serve():

  async with DaprClientAsync() as a:
      log.info(f"{a._channel.__class__}")




  server = app._server
  with DaprClient() as dapr:
    # Observer current prices to simulate buy/sell operations using last market values
    # just to simplify operations
    # Proper implementation (guessing prices, postponing operation) will be imlemented later on
    @app.subscribe(pubsub_name='pubsub', topic=d.as_topic_name(me.MarketChangedEvent))
    def on_something(event: v1.Event) -> Optional[TopicEventResponse]:
        as_json = cast(bytes, event.data).decode('UTF-8')
        as_dict = json.loads(as_json)
        event_typed = me.MarketChangedEvent._construct(as_dict)
        with lock:
            key = as_key(event_typed)
            market[key] = event_typed
            pass

        return TopicEventResponse("success")

    add_AgentServicer_to_server(MyService(dapr), server)
    app.run(APP_PORT)

def as_key(item: me.MarketChangedEvent):
    return f"{item.ticker}-{item.date}"

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(serve())
