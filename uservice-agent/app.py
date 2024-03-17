from concurrent import futures
from datetime import date, timedelta
import datetime
from io import BytesIO
import logging
import os
from typing import Optional
from venv import logger
from dapr.clients.grpc._response import TopicEventResponse

from cloudevents.sdk.event import v1
from dapr.ext.grpc import App

from dapr.clients import DaprClient
from avro import datafile, io
import scheduler_rpc.onlexnet.ptn.scheduler.events as events
import onlexnet.Dapr as d
import pandas as pd


APP_PORT=os.getenv('APP_PORT')
log = logging.getLogger("myapp")

app = App()

# Default subscription for a topic
@app.subscribe(pubsub_name='pubsub', topic='onlexnet:v1:onlexnet.ptn.scheduler.events.BalanceReportRequestedEvent')
def mytopic(event: v1.Event) -> Optional[TopicEventResponse]:
    # Returning None (or not doing a return explicitly) is equivalent
    # to returning a TopicEventResponse("success").
    # You can also return TopicEventResponse("retry") for dapr to log
    # the message and retry delivery later, or TopicEventResponse("drop")
    # for it to drop the message

    # store financial result raport as requested by the event

    # list of name, degree, score
    nme = ["aparna", "pankaj", "sudhir", "Geeku"]
    deg = ["MBA", "BCA", "M.Tech", "MBA"]
    scr = [90, 40, 80, 98]

    # dictionary of lists
    dict = {'name': nme, 'degree': deg, 'score': scr}

    df = pd.DataFrame(dict)
    asset_name = "test"
    asset_folder = os.path.join('.reports', asset_name.lower())
    os.makedirs(asset_folder, exist_ok=True)  # create folder, if exists
    start_date = datetime()
    file_name = f"{start_date.strftime('%Y-%m-%d')}.csv"
    file_path = os.path.join(asset_folder, file_name)
    df.to_csv(file_path)


    df.to_csv()

    return TopicEventResponse("success")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(APP_PORT)
