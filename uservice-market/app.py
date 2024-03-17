import asyncio
from concurrent import futures
from io import BytesIO
import logging
import os
import signal
import sys
import uuid
from venv import logger
import grpc
import fastavro
import json
from datetime import date

from pandas import DataFrame

import src.YahooFinance as yf

from dapr.clients import DaprClient
from avro import datafile, io
import market_rpc.onlexnet.pdt.market.events as events
APP_PORT=os.getenv('APP_PORT', 50052)
log = logging.getLogger("myapp")

async def serve(df: DataFrame):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    server.add_insecure_port(f"[::]:{APP_PORT}")
    server.start()

    with DaprClient() as dc:
        
        schema_prefix = "onlexnet:v1"
        topic_name = f"{schema_prefix}:{events.MarketChangedEvent.RECORD_SCHEMA.fullname}"

        for index, row in df.iterrows():
            date = row['date']
            date_as_year = date.year * 10_000 + date.month * 100 + date.day
            event = events.MarketChangedEvent(date = date_as_year)
            event_as_str = str(event)
            event_as_dict = event.to_avro_writable()
            as_json = json.dumps(event_as_dict)
            fastavro.json_writer
            resp = dc.publish_event(pubsub_name="pubsub", topic_name=topic_name, data = as_json, data_content_type="application/json")
            logging.info(f"Event sent: {event_as_str}")
            await asyncio.sleep(0.01)

    server.wait_for_termination()

def signal_handler(sig, frame):
    logger.warn('You pressed Ctrl+C!')
    sys.exit(0)

if __name__ == '__main__':

    ctx = yf.LoadContext(date(2020, 1, 1), date(2020, 12, 31), "msft")
    data = yf.load(ctx)

    logging.basicConfig(level=logging.DEBUG)

    logger.info(f"port: {APP_PORT}")
    
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(serve(data)),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    signal.signal(signal.SIGINT, signal_handler)