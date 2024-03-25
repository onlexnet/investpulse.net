import asyncio
from concurrent import futures
from io import BytesIO
import logging
import os
import signal
import sys
import time
from typing import Optional, cast
import uuid
from venv import logger
import grpc
import fastavro
import json
from datetime import date

from pandas import DataFrame

from src.DaprInterceptor import add_header
import src.YahooFinance as yf

from dapr.clients import DaprClient
from avro import datafile, io
import market_rpc.onlexnet.pdt.market.events as events
import scheduler_rpc.onlexnet.ptn.scheduler.events as events_scheduler
from scheduler_rpc.schema_pb2_grpc import TimeSchedulerStub
from scheduler_rpc.schema_pb2 import TimeClient
import scheduler_rpc.onlexnet.ptn.scheduler.test.events as scheduler_test
import onlexnet.dapr as d
from dapr.ext.grpc import App
from cloudevents.sdk.event import v1
from dapr.clients.grpc._response import TopicEventResponseStatus, TopicEventResponse

APP_PORT=os.getenv('APP_PORT', 50000)
DAPR_GRPC_PORT=os.getenv('DAPR_GRPC_PORT', 0)

app = App()


# in the future we would like to listen data directly from Yahoo
# right now, we are working on simulated time so is enough to preload data from Yahoo
# and serve the data when time 'passed'
def preload_data() -> DataFrame:
    ctx = yf.LoadContext(date(2020, 1, 1), date(2023, 12, 31), "msft")
    data = yf.load(ctx)
    return data

async def serve(df: DataFrame):
    dapr_interceptor = add_header('dapr-app-id', 'scheduler')

    channel = grpc.insecure_channel(f"localhost:{DAPR_GRPC_PORT}")
    scheduler_channel = grpc.intercept_channel(channel, dapr_interceptor) 
    stub = TimeSchedulerStub(scheduler_channel)
    stub.tick(TimeClient())

    with DaprClient() as dc:
        @app.subscribe(pubsub_name='pubsub', topic=d.as_topic_name(events_scheduler.NewTime))
        def mytopic(event: v1.Event) -> Optional[TopicEventResponse]:
            # Returning None (or not doing a return explicitly) is equivalent
            # to returning a TopicEventResponse("success").
            # You can also return TopicEventResponse("retry") for dapr to log
            # the message and retry delivery later, or TopicEventResponse("drop")
            # for it to drop the message

            as_json = cast(bytes, event.data).decode('UTF-8')
            as_dict = json.loads(as_json)
            event_typed = events_scheduler.NewTime.from_obj(as_dict)
            correlation_id = event_typed.correlationId
            d.publish(dc, scheduler_test.NewTimeApplied(correlation_id))
            return TopicEventResponse(TopicEventResponseStatus.success)


    #     for index, row in df.iterrows():
    #         date = row['date']
    #         date_as_year = date.year * 10_000 + date.month * 100 + date.day
    #         event = events.MarketChangedEvent(date = date_as_year)
    #         d.publish(dc, event)
    #         logging.info(f"Event sent: {event}")
    #         await asyncio.sleep(0.01)
    #     pass        
    
        app.run(int(APP_PORT))


def signal_handler(sig, frame):
    logger.warn('You pressed Ctrl+C!')
    sys.exit(0)

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    logger.info(f"port: {APP_PORT}")
    
    yahoo_data = preload_data()
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(serve(yahoo_data)),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    signal.signal(signal.SIGINT, signal_handler)