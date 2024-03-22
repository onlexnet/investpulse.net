import asyncio
from concurrent import futures
from datetime import date, timedelta
import logging
import os
from venv import logger

from dapr.clients import DaprClient
from avro import datafile, io
import scheduler_rpc.onlexnet.ptn.scheduler.events as events
import onlexnet.Dapr as d

from scheduler_rpc.schema_pb2_grpc import TimeSchedulerServicer, add_TimeSchedulerServicer_to_server
import scheduler_rpc.schema_pb2 as proto

from concurrent import futures
import logging
import os
import grpc
from grpc_reflection.v1alpha import reflection


APP_PORT=os.getenv('APP_PORT', 50000)
log = logging.getLogger("myapp")

class TimeSchedulerGrpc(TimeSchedulerServicer):
    def tick(self, request: proto.TimeClient, context):
        log.info(request)
        reply = proto.NewTime()
        return reply



def number_of_expected_clients() -> int:
    ENV_NAME_NUMBER_OF_TIME_CLIENTS = 'NUMBER_OF_TIME_CLIENTS'
    CLIENTS=os.getenv(ENV_NAME_NUMBER_OF_TIME_CLIENTS)
    if (CLIENTS == 'REAL'):
        return 0
    if (CLIENTS == None):
        raise ValueError(f"Env variable 'ENV_NAME_NUMBER_OF_TIME_CLIENTS' is not defined")
    return int(CLIENTS)


async def serve():

    with DaprClient() as dc:
        start_date = date(2001, 1, 1)
        end_date = date(2001, 2, 2)

        current_date = start_date

        while current_date <= end_date:

            current_date_as_int = current_date.year * 10_000 + current_date.month * 100 + current_date.day

            event = events.TimeChangedEvent(current_date_as_int)
            logging.info(event)

            d.publish(dc, event)

            current_date += timedelta(days=1)
            await asyncio.sleep(0.1)

            report_event = events.BalanceReportRequestedEvent()

        d.publish(dc, report_event)




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














def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_PingServiceServicer_to_server(MyClass(), server)

    # the reflection service will be aware of "Greeter" and "ServerReflection" services.
    # source: https://github.com/grpc/grpc/blob/master/doc/python/server_reflection.md
    SERVICE_NAMES = (
        app1_pb2.DESCRIPTOR.services_by_name['PingService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    server.add_insecure_port(f"[::]:{APP_PORT}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    log.setLevel(logging.INFO)

    log.info(f"port: {APP_PORT}")
    serve()