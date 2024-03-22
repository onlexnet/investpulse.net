from asyncio import Lock
from typing import Callable, List, TypeAlias
import scheduler_rpc.schema_pb2 as proto


ClientProxy: TypeAlias = Callable[[proto.NewTime], None]

class ClientsHub:
    """
    Waits for predicted number of clients, and next notifies all of them about time changes.
    """

    __clients: List[ClientProxy] = list()
    __scope_from: proto.NewTime

    __lock = Lock()

    def __init__(self, numer_of_clients: int, scope_from: proto.NewTime):
        self.number_of_clients = numer_of_clients
        self.__scope_from = scope_from

    async def add_client(self, client: ClientProxy):
        """
        Waits for all clients and starts emits events automatically
        """
        async with self.__lock:
            self.__clients.append(client)

        now = self.__scope_from
        for client in self.__clients:
            client(now)

