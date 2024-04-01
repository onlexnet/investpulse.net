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

APP_PORT=os.getenv('APP_PORT', 8080)

app = App()

def main():
    with DaprClient() as dc:
        # Default subscription for a topic

        @app.subscribe(pubsub_name='pubsub', topic=d.as_topic_name(signal_events.Order))
        def on_TimeChangedEventClass(event: v1.Event) -> Optional[TopicEventResponse]:

            as_json = cast(bytes, event.data).decode('UTF-8')
            as_dict = json.loads(as_json)

            event_typed = signal_events.Order._construct(as_dict)
            log.info(f"SPARTAAAA {event_typed}")

            return TopicEventResponse("success")
        app.run(int(APP_PORT))

if __name__ == '__main__':
    main()
