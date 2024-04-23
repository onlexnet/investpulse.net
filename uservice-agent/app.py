import asyncio
import asyncio.log
from concurrent import futures
from dataclasses import dataclass
from datetime import date, timedelta
import datetime
from io import BytesIO
from dapr.proto import appcallback_service_v1, common_v1, appcallback_v1
import logging
import grpc
import grpc.experimental.aio
import json
import os
import struct
from typing import Optional, cast
from dapr.clients.grpc._response import TopicEventResponse

from dapr.proto.runtime.v1.appcallback_pb2_grpc import AppCallbackServicer, add_AppCallbackServicer_to_server, AppCallbackHealthCheckServicer, add_AppCallbackHealthCheckServicer_to_server
from google.protobuf.empty_pb2 import Empty

from cloudevents.sdk.event import v1

from dapr.aio.clients import DaprClient
from avro import datafile, io
import scheduler_rpc.onlexnet.ptn.scheduler.events as events
import market_rpc.onlexnet.pdt.market.events as me
import onlexnet.dapr as d
import pandas as pd
from agent_rpc.schema_pb2_grpc import AgentServicer, add_AgentServicer_to_server
from agent_rpc.schema_pb2 import State, OrderBook, Finished, BuyOrder, SellOrder
from dapr.proto.runtime.v1.dapr_pb2 import _sym_db
from grpc._server import _Context
from grpc._cython.cygrpc import _ServicerContext

from src.apicallback import ListTopicSubscriptionsResponse, TopicSubscription


APP_PORT=int(os.getenv('APP_PORT', 50000))
from asyncio.log import logger as log

class MyAppCallbackHealthCheckServicer(AppCallbackHealthCheckServicer):
  async def HealthCheck(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')




class MyCallbacks(AppCallbackServicer):
  async def OnInvoke(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented! :)')
    raise NotImplementedError('Method not implemented! :)')

  async def ListTopicSubscriptions(self, request: Empty, context: _ServicerContext):
    topic1 = d.as_topic_name(me.MarketChangedEvent)
    ts1 = appcallback_v1.TopicSubscription(pubsub_name = "pubsub", topic = topic1)
    return appcallback_v1.ListTopicSubscriptionsResponse(subscriptions = [ts1])


  async def OnTopicEvent(self, request: appcallback_v1.TopicEventRequest, context) -> appcallback_v1.TopicEventResponse:
    id: str = request.id # "6d85382e-5023-42d2-a146-589b104a5a91"
    source: str = request.source # "app1"
    type: str = request.type # "com.dapr.event.sent"
    spec_version: str = request.spec_version # "1.0"
    data_content_type: str = request.data_content_type # "application/json"
    data: str = request.data # "{\"orderId\":\"100\"}"
    topic: str = request.topic # "onlexnet:v1:onlexnet.pdt.market.events.MarketChangedEvent"
    pubsub_name: str = request.pubsub_name # "pubsub"
    extensions: list[tuple[str, str]] = request.extensions.items()

    return appcallback_v1.TopicEventResponse(status = 0) # success

  async def ListInputBindings(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented! :)')
    raise NotImplementedError('Method not implemented! :)')

  async def OnBindingEvent(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented! :)')
    raise NotImplementedError('Method not implemented! :)')


class MyService(AgentServicer):
    def __init__(self, dapr: DaprClient) -> None:
        self._dapr = dapr

    async def buy(self, request: BuyOrder, context: _Context) -> State:
        log.info("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        # awaitr self._dapr.save_state()
        log.info(request)
        # load current state

        return State(orderBook=OrderBook(), finished=Finished(), budget=2000)

    async def sell(self, request: SellOrder, context: _Context) -> State:
        log.info("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
        return State(orderBook=OrderBook(), finished=Finished(), budget=2000)


# @app.subscribe(pubsub_name='pubsub', topic=d.as_topic_name(events.BalanceReportRequestedEvent))
# def on_BalanceReportRequestedEvent(event: v1.Event) -> Optional[TopicEventResponse]:
#     # Returning None (or not doing a return explicitly) is equivalent
#     # to returning a TopicEventResponse("success").
#     # You can also return TopicEventResponse("retry") for dapr to log
#     # the message and retry delivery later, or TopicEventResponse("drop")
#     # for it to drop the message

#     # store financial result raport as requested by the event

#     # list of name, degree, score
#     nme = ["aparna", "pankaj", "sudhir", "Geeku"]
#     deg = ["MBA", "BCA", "M.Tech", "MBA"]
#     scr = [90, 40, 80, 98]

#     # dictionary of lists
#     dict = {'name': nme, 'degree': deg, 'score': scr}

#     df = pd.DataFrame(dict)
#     asset_name = "test"
#     asset_folder = os.path.join('.reports', asset_name.lower())
#     os.makedirs(asset_folder, exist_ok=True)  # create folder, if exists
#     start_date = datetime.datetime.now()
#     file_name = f"{start_date.strftime('%Y-%m-%d')}.csv"
#     file_path = os.path.join(asset_folder, file_name)
#     df.to_csv(file_path)


#     df.to_csv()

#     return TopicEventResponse("success")

async def serve():
  grpc.experimental.aio.init_grpc_aio()
  server = grpc.experimental.aio.server()
  server.add_insecure_port(f"[::]:{APP_PORT}")

  async with DaprClient() as dapr:
    # Observer current prices to simulate buy/sell operations using last market values
    # just to simplify operations
    # Proper implementation (guessing prices, postponing operation) will be imlemented later on
    # @app.subscribe(pubsub_name='pubsub', topic=d.as_topic_name(me.MarketChangedEvent))
    # def on_MarketChangedEvent(event: v1.Event) -> Optional[TopicEventResponse]:
    #     as_json = cast(bytes, event.data).decode('UTF-8')
    #     as_dict = json.loads(as_json)
    #     event_typed = me.MarketChangedEvent._construct(as_dict)

    #     ticker = event_typed.ticker
    #     price = event_typed.adjClose # naive approximation just to have some proce before doing better prediction
    #     date = event_typed.date

    #     dapr.save_state("statestore", f"price:{ticker}", struct.pack('d', price))

    #     return TopicEventResponse("success")

    add_AgentServicer_to_server(MyService(dapr), server)
    add_AppCallbackServicer_to_server(MyCallbacks(), server)
    add_AppCallbackHealthCheckServicer_to_server(MyAppCallbackHealthCheckServicer(), server)

    await server.start()
    await server.wait_for_termination()


def as_key(item: me.MarketChangedEvent):
    return f"{item.ticker}-{item.date}"

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
