import grpc
import onlexnet.dapr as d
import signals_rpc.onlexnet.pdt.signals.events as signal_events
import json
from src.logger import log
import os
from typing import Optional, cast
from dapr.clients.grpc._response import TopicEventResponse

from cloudevents.sdk.event import v1
from dapr.ext.grpc import App

from dapr.clients import DaprClient
import onlexnet.dapr as d

from agent_rpc.schema_pb2_grpc import AgentStub
from agent_rpc.schema_pb2 import BuyOrder, BuyMax

APP_PORT=os.getenv('APP_PORT', 8080)
DAPR_GRPC_PORT=os.getenv('DAPR_GRPC_PORT', 0)
APP_ID=cast(str, os.getenv('APP_ID'))

app = App()

def main():
    with DaprClient() as dc:
        # Default subscription for a topic

        agent_interceptor = d.add_header('dapr-app-id', 'agent')
        channel = grpc.insecure_channel(f"localhost:{DAPR_GRPC_PORT}")
        agent_channel = grpc.intercept_channel(channel, agent_interceptor)
        agent = AgentStub(agent_channel)
        agent.buy(BuyOrder(clientId=APP_ID, ticker="msft", buyMax=BuyMax()))

        @app.subscribe(pubsub_name='pubsub', topic=d.as_topic_name(signal_events.Order))
        def on_Order(event: v1.Event) -> Optional[TopicEventResponse]:

            as_json = cast(bytes, event.data).decode('UTF-8')
            as_dict = json.loads(as_json)

            event_typed = signal_events.Order._construct(as_dict)
            log.info(f"SPARTAAAA1 {event_typed}")



            # TODO:
            # - guess price
            return TopicEventResponse("success")

        app.run(int(APP_PORT))

if __name__ == '__main__':
    main()
