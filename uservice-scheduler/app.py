import asyncio
from concurrent import futures
from datetime import date, timedelta
from io import BytesIO
import logging
import os
import signal
import sys
from venv import logger
import fastavro
import json

from dapr.clients import DaprClient
from avro import datafile, io
import scheduler_rpc.onlexnet.ptn.scheduler.events as events
APP_PORT=os.getenv('APP_PORT', 500)
log = logging.getLogger("myapp")

async def serve():

    with DaprClient() as dc:
        start_date = date(2001, 1, 1)
        end_date = date(2001, 2, 2)

        current_date = start_date

        while current_date <= end_date:

            current_date_as_int = current_date.year * 10_000 + current_date.month * 100 + current_date.day

            event = events.TimeChangedEvent(current_date_as_int)
            logging.info(event)

            schema_prefix = "onlexnet:v1"
            topic_name = f"{schema_prefix}:{event.RECORD_SCHEMA.fullname}"
            event_as_dict = event.to_avro_writable()
            as_json = json.dumps(event_as_dict)
            dc.publish_event(pubsub_name="pubsub", topic_name=topic_name, data = as_json, data_content_type="application/json", publish_metadata={ "ttlInSeconds": "10" })
            logging.info(f"Event sent: {event}")

            current_date += timedelta(days=1)
            await asyncio.sleep(0.3)




    # server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    logger.info(f"port: {APP_PORT}")
    
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(serve()),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
