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
import onlexnet.dapr as d

APP_PORT=os.getenv('APP_PORT', 50052)
log = logging.getLogger("myapp")

# in the future we would like to listen data directly from Yahoo
# right now, we are working on simulated time so is enough to preload data from Yahoo
# and serve the data when time 'passed'
def preload_data() -> DataFrame:
    ctx = yf.LoadContext(date(2020, 1, 1), date(2023, 12, 31), "msft")
    data = yf.load(ctx)
    return data

async def serve(df: DataFrame):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    server.add_insecure_port(f"[::]:{APP_PORT}")
    server.start()

    with DaprClient() as dc:
        
        for index, row in df.iterrows():
            date = row['date']
            date_as_year = date.year * 10_000 + date.month * 100 + date.day
            event = events.MarketChangedEvent(date = date_as_year)
            d.publish(dc, event)
            logging.info(f"Event sent: {event}")
            await asyncio.sleep(0.01)

    server.wait_for_termination()

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