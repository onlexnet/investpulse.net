import asyncio
from concurrent import futures
import logging
import os
import signal
import sys
from venv import logger
import grpc

from dapr.clients import DaprClient
from market_rpc.onlexnet.market.events import MarketChangedEvent
from avro import datafile, io

APP_PORT=os.getenv('APP_PORT', 50052)
log = logging.getLogger("myapp")

async def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    server.add_insecure_port(f"[::]:{APP_PORT}")
    server.start()

    with DaprClient() as dc:
        event = MarketChangedEvent(date = 20010203)
        event_as_str = str(event)
        event_as_bytes = event.to_avro_writable()
        logging.info("sparta")
        logging.info(f"Event as string: {event_as_str}")
        print(event_as_str.__class__)

        while True:
            await asyncio.sleep(1)
            # resp = dc.publish_event(pubsub_name="pubsub", topic_name="TOPIC_A", data = event_as_str, data_content_type="application/avro")
            resp = dc.publish_event(pubsub_name="pubsub", topic_name="TOPIC_A", data = event_as_str)
            logging.info(f"Event sent: {event_as_str}")

    server.wait_for_termination()

def signal_handler(sig, frame):
    logger.warn('You pressed Ctrl+C!')
    sys.exit(0)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    logger.info(f"port: {APP_PORT}")
    
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(serve()),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    signal.signal(signal.SIGINT, signal_handler)