from concurrent import futures
import logging
import os
import grpc
from grpc_reflection.v1alpha import reflection

from .lib.app1_rpc.app1_pb2 import PingResponse

from .lib.app1_rpc.app1_pb2_grpc import PingServiceServicer, add_PingServiceServicer_to_server
from lib.app1_rpc import app1_pb2

APP_PORT=os.getenv('APP_PORT', 50051)
log = logging.getLogger("myapp")

class MyClass(PingServiceServicer):

    def ping(self, request, context):
        log.info(request)
        reply = PingResponse(message="Hello Łosiu")
        return reply

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