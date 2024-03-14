from concurrent import futures
import logging
import os
import grpc

from market_rpc.market_pb2 import MarketChangedEvent
from dapr.clients import DaprClient

APP_PORT=os.getenv('APP_PORT', 50052)
log = logging.getLogger("myapp")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    server.add_insecure_port(f"[::]:{APP_PORT}")
    server.start()

    with DaprClient() as dc:
        event = MarketChangedEvent(date=20200102, open=1, close=2, low=3, high=4, adj_close=5)
        event_as_bytes = event.SerializeToString()
        logging.log("sparta")
        logging.log(f"bytes: {event_as_bytes}")
        print("spartaaa")
        print(event_as_bytes.__class__)
        resp = dc.publish_event(pubsub_name="pubsub", topic_name="TOPIC_A", data = event_as_bytes)

    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    log.setLevel(logging.INFO)

    log.info(f"port: {APP_PORT}")
    serve()