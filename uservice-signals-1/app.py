from asyncio.log import logger
from concurrent import futures
from datetime import date, timedelta
import datetime
import json
import logging
from logging.handlers import QueueHandler, QueueListener
import os
import threading
from typing import Optional, cast
from dapr.clients.grpc._response import TopicEventResponse

from cloudevents.sdk.event import v1
from dapr.ext.grpc import App

from dapr.clients import DaprClient
import scheduler_rpc.onlexnet.ptn.scheduler.events as events
import onlexnet.dapr as d
import pandas as pd
import market_rpc.onlexnet.pdt.market.events as market_events
# the queue is thread safe
from queue import Queue

APP_PORT=os.getenv('APP_PORT')

app = App()

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

lock = threading.Lock()
df = pd.DataFrame()

# Default subscription for a topic
@app.subscribe(pubsub_name='pubsub', topic=d.as_topic_name(market_events.MarketChangedEvent))
def onTimeChangedEventClass(event: v1.Event) -> Optional[TopicEventResponse]:

    as_json = cast(bytes, event.data).decode('UTF-8')
    as_dict = json.loads(as_json)
    event_typed = market_events.MarketChangedEvent.from_obj(as_dict)

    with lock:
        last_index = len(df)
        df.loc[last_index] = as_dict

    logging.info("SPARTAAAAAAAAAAAAAA")

    # Returning None (or not doing a return explicitly) is equivalent
    # to returning a TopicEventResponse("success").
    # You can also return TopicEventResponse("retry") for dapr to log
    # the message and retry delivery later, or TopicEventResponse("drop")
    # for it to drop the message

    # store financial result raport as requested by the event

    # list of name, degree, score
    # nme = ["aparna", "pankaj", "sudhir", "Geeku"]
    # deg = ["MBA", "BCA", "M.Tech", "MBA"]
    # scr = [90, 40, 80, 98]

    # # dictionary of lists
    # dict = {'name': nme, 'degree': deg, 'score': scr}

    # df = pd.DataFrame(dict)
    # asset_name = "test"
    # asset_folder = os.path.join('.reports', asset_name.lower())
    # os.makedirs(asset_folder, exist_ok=True)  # create folder, if exists
    # start_date = datetime()
    # file_name = f"{start_date.strftime('%Y-%m-%d')}.csv"
    # file_path = os.path.join(asset_folder, file_name)
    # df.to_csv(file_path)


    # df.to_csv()

    return TopicEventResponse("success")

if __name__ == '__main__':
    app.run(int(APP_PORT))
