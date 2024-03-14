from concurrent import futures
import logging
import os
import grpc

from dapr.clients import DaprClient
from market_rpc.onlexnet.market.events import MarketChangedEvent
from avro import datafile, io

APP_PORT=os.getenv('APP_PORT', 50052)
log = logging.getLogger("myapp")

def serve():
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
        resp = dc.publish_event(pubsub_name="pubsub", topic_name="TOPIC_A", data = event_as_str, data_content_type="application/avro")

    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    log.setLevel(logging.INFO)

    log.info(f"port: {APP_PORT}")
    serve()