from datetime import datetime
import onlexnet.dapr as d
import scheduler_rpc.onlexnet.ptn.scheduler.test.events as scheduler_test
import json
from src.logger import log
import os
from typing import Optional, cast
from dapr.clients.grpc._response import TopicEventResponse

from cloudevents.sdk.event import v1
from dapr.ext.grpc import App

from dapr.clients import DaprClient
import onlexnet.dapr as d
import market_rpc.onlexnet.pdt.market.events as market_events
# the queue is thread safe

from onlexnet.convert import from_datetime5
import src.data as data
from src.market import Publisher
import src.market as market


APP_PORT=os.getenv('APP_PORT', 8080)

app = App()

def main():
    with DaprClient() as dc:
        # Default subscription for a topic

        sender: Publisher = lambda x: d.publish(dc, "pubsub", x)
        @app.subscribe(pubsub_name='pubsub', topic=d.as_topic_name(market_events.MarketChangedEvent))
        def on_MarketChangedEvent(event: v1.Event) -> Optional[TopicEventResponse]:

            as_json = cast(bytes, event.data).decode('UTF-8')
            as_dict = json.loads(as_json)
            assert isinstance(as_dict, dict)

            event_typed = market_events.MarketChangedEvent._construct(as_dict)
            assert isinstance(event_typed, market_events.MarketChangedEvent)

            # TODO: add data only if it does not exists AND has 'close' value
            # so that we may avoid duplicates
            # when new data is added, create proper BUY or SELL event

            new_event = data.create_events(event_typed)
            # do not fix error of types - it works perfectly
            # it needs to be moved to spearated place and avro deserialization should be also out of domain logic
            when5 = market_events.datetime5._construct(event_typed.when)

            when = from_datetime5(when5.yyyymmdd, when5.hhmm)
            # now = datetime(event_typed.)
            if new_event.name != 'NONE':
                market.send(new_event, sender, when)

            d.cont(dc, "pubsub", scheduler_test.NewTimeApplied("correlation_id", 0), event)

            # Returning None (or not doing a return explicitly) is equivalent
            # to returning a TopicEventResponse("success").
            # You can also return TopicEventResponse("retry") for dapr to log
            # the message and retry delivery later, or TopicEventResponse("drop")
            # for it to drop the message

            # store financial result raport as requested by the event

            return TopicEventResponse("success")
        app.run(int(APP_PORT))

if __name__ == '__main__':
    main()
