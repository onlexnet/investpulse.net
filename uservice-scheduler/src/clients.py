from asyncio import Lock
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Awaitable, Callable, List, TypeAlias
from uuid import uuid4
import scheduler_rpc.schema_pb2 as proto

from src.mapper import from_dto, normalize, to_dto


ClientProxy: TypeAlias = Callable[[proto.NewTime], Awaitable[None]]

class ClientsHub:
    """
    Waits for predicted number of clients, and next notifies all of them about time changes.
    """

    __clients: List[ClientProxy] = list()
    __lock = Lock()
    __now: datetime


    def __init__(self, numer_of_clients: int, scope_from: datetime, scope_to: datetime):
        self.number_of_clients = numer_of_clients
        self.__now = normalize(scope_from)
        self.__scope_to = scope_to

    async def add_client(self, client: ClientProxy):
        """
        Waits for all clients and starts emits events automatically
        """

        async with self.__lock:
            self.__clients.append(client)

        await self.__dispatch_time();
    
    async def on_client_ack(self, correlation_id: str):

        """
        the method will be ignored on prod as I do not see any special case
        in tests it is used to wait with next time signal when all clients already applied side effects of the previous signal
        """
        async with self.__lock:
            if self.__acks_to_confirm > 0:
                self.__acks_to_confirm -= 1
            else:
                raise ValueError("Unexpected")

        # if we are waiting for more confirmations, lets skip next step
        if self.__acks_to_confirm > 0:
            return
        
        self.__next_time()
        await self.__dispatch_time()
        
    def __next_time(self):
        now = self.__now
        time_delta = timedelta(minutes=1)
        new_datetime = now + time_delta
        self.__now = new_datetime
    
    async def __dispatch_time(self):
        for client in self.__clients:
            correlation_id = str(uuid4())
            now = self.__now
            event = to_dto(now, correlation_id)
            # all clients has to confirm time message
            self.__acks_to_confirm = self.number_of_clients
            await client(event)
