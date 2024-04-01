import functools
import json
from cloudevents.sdk.event import v1
import asyncio
from concurrent import futures
from datetime import datetime, timedelta
import logging
import os
from typing import Optional, cast
from venv import logger
from dapr.clients.grpc._response import TopicEventResponseStatus, TopicEventResponse

from dapr.clients import DaprClient
from avro import datafile, io
import scheduler_rpc.onlexnet.ptn.scheduler.events as events
import onlexnet.dapr as d

from scheduler_rpc.schema_pb2_grpc import TimeSchedulerServicer, add_TimeSchedulerServicer_to_server
import scheduler_rpc.schema_pb2 as proto

from concurrent import futures
import logging
import os
import grpc
from grpc_reflection.v1alpha import reflection

from src.calls import invocation_counter
from src.clients import ClientsHub, Sender
from src.mapper import to_dto
from src.models import TimeTick

from dapr.ext.grpc import App

APP_PORT=os.getenv('APP_PORT', 50000)
log = logging.getLogger("myapp")

class TimeSchedulerGrpc(TimeSchedulerServicer):

    def __init__(self, sender: Sender):
        start_date = datetime(2014, 1, 1)
        end_date = datetime(2023, 12, 31, 23, 59)
        self.hub = ClientsHub(1, start_date, end_date, sender)

    def send(self, correlation_id: str):
        self.hub.on_client_ack(correlation_id)

    def tick(self, request: proto.TimeClient, context):
        log.info(f"request: {request}")
        self.hub.add_client()

        reply = proto.ClientTag()
        return reply



def number_of_expected_clients() -> int:
    ENV_NAME_NUMBER_OF_TIME_CLIENTS = 'NUMBER_OF_TIME_CLIENTS'
    CLIENTS=os.getenv(ENV_NAME_NUMBER_OF_TIME_CLIENTS)
    if (CLIENTS == 'REAL'):
        return 0
    if (CLIENTS == None):
        raise ValueError(f"Env variable 'ENV_NAME_NUMBER_OF_TIME_CLIENTS' is not defined")
    return int(CLIENTS)

app = App()
known_clients = number_of_expected_clients()


async def main():
    clients_to_confirm: int
    server = app._server
    with DaprClient() as dc:

        @invocation_counter
        def send(x: TimeTick):
            event = to_dto(x.now, x.correlation_id)
            nonlocal clients_to_confirm
            clients_to_confirm = known_clients
            d.publish(dc, "pubsub", event)

        service = TimeSchedulerGrpc(send)
        add_TimeSchedulerServicer_to_server(service, server)
        
        @app.subscribe(pubsub_name='pubsub', topic=d.as_topic_name(events.NewTimeApplied))
        def onNewTimeApplied(event: v1.Event) -> Optional[TopicEventResponse]:
            as_json = cast(bytes, event.data).decode('UTF-8')
            as_dict = json.loads(as_json)
            event_typed = events.NewTimeApplied.from_obj(as_dict)
            correlation_id = event_typed.correlationId
            additional_clients = event_typed.additionalClients or 0

            nonlocal clients_to_confirm
            clients_to_confirm = clients_to_confirm - 1 + additional_clients
            if clients_to_confirm > 0:
                return

            service.send(correlation_id)

        # report_event = events.BalanceReportRequestedEvent()
        # d.publish(dc, report_event)

        # the reflection service will be aware of "Greeter" and "ServerReflection" services.
        # source: https://github.com/grpc/grpc/blob/master/doc/python/server_reflection.md
        SERVICE_NAMES = (
            proto.DESCRIPTOR.services_by_name['TimeScheduler'].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)
        app.run(int(APP_PORT))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    logger.info(f"port: {APP_PORT}")

    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(main()),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
