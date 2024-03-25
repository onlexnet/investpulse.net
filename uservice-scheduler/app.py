import asyncio
from concurrent import futures
from datetime import datetime, timedelta
import logging
import os
from venv import logger

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

from src.clients import ClientsHub, Sender
from src.mapper import to_dto
from src.models import TimeTick


APP_PORT=os.getenv('APP_PORT', 50000)
log = logging.getLogger("myapp")

class TimeSchedulerGrpc(TimeSchedulerServicer):

    def __init__(self, sender: Sender):
        start_date = datetime(2001, 1, 1)
        end_date = datetime(2001, 2, 2)
        self.hub = ClientsHub(1, start_date, end_date, sender)

    async def send(self, tick: TimeTick):
        pass

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


async def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    with DaprClient() as dc:

        def send(x: TimeTick):
            event = to_dto(x.now, x.correlation_id)
            d.publish(dc, event)
        service = TimeSchedulerGrpc(send)
        add_TimeSchedulerServicer_to_server(service, server)
        
        # report_event = events.BalanceReportRequestedEvent()
        # d.publish(dc, report_event)

        # the reflection service will be aware of "Greeter" and "ServerReflection" services.
        # source: https://github.com/grpc/grpc/blob/master/doc/python/server_reflection.md
        SERVICE_NAMES = (
            proto.DESCRIPTOR.services_by_name['TimeScheduler'].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)

        server.add_insecure_port(f"[::]:{APP_PORT}")
        server.start()
        server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    logger.info(f"port: {APP_PORT}")

    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(main()),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
