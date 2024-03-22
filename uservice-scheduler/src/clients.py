from asyncio import Lock
from dataclasses import dataclass
from typing import Awaitable, Callable, List, TypeAlias
from uuid import uuid4
import scheduler_rpc.schema_pb2 as proto


ClientProxy: TypeAlias = Callable[[proto.NewTime], Awaitable[None]]

@dataclass
class DateTime:
    yyyymmdd: int
    hhmm: int

class ClientsHub:
    """
    Waits for predicted number of clients, and next notifies all of them about time changes.
    """

    __clients: List[ClientProxy] = list()

    __lock = Lock()

    def __init__(self, numer_of_clients: int, scope_from: DateTime, scope_to: DateTime):
        self.number_of_clients = numer_of_clients
        self.__scope_from = scope_from
        self.__scope_to = scope_to

    async def add_client(self, client: ClientProxy):
        """
        Waits for all clients and starts emits events automatically
        """

        async with self.__lock:
            self.__clients.append(client)

        now = self.__scope_from
        for client in self.__clients:
            correlation_id = str(uuid4())
            event = proto.NewTime(yyyymmdd=now.yyyymmdd, hhmm=now.hhmm, correlationId=correlation_id)
            await client(event)
    
    async def on_client_ack(self, correlation_id: str):
        pass

