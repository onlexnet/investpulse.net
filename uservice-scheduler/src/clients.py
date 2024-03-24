from asyncio import Lock
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import AsyncIterable, Awaitable, Callable, List, TypeAlias
from uuid import uuid4

from src.mapper import normalize, to_dto
from src.models import Sender, TimeTick

class ClientsHub:
    """
    Waits for predicted number of clients, and next notifies all of them about time changes.
    """

    __lock = Lock()
    __now: datetime
    __sender: Sender


    def __init__(self, numer_of_clients: int, scope_from: datetime, scope_to: datetime, sender: Sender):
        self.number_of_clients = numer_of_clients
        self.__now = normalize(scope_from)
        self.__scope_to = scope_to
        self.__sender = sender

    async def add_client(self):
        """
        Waits for all clients and starts emits events automatically
        """

        # async with self.__lock:
        #     self.__clients.append(client)

        # TODO dispatch time only when all expected clients are connected

        await self.__dispatch_time();
    
    async def on_client_ack(self, correlation_id: str):
        """
        the method will be ignored on prod as I do not see any special case
        in tests it is used to wait with next time signal when all clients already applied side effects of the previous signal
        """

        # TODO
        # check if correlation_id is valid, it means: same as used with latesst NewTime message to clients
        
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
        correlation_id = str(uuid4())
        now = self.__now
        event = to_dto(now, correlation_id)
        # all know clients has to confirm time message which we are going to send
        self.__correlation_id = correlation_id
        self.__acks_to_confirm = self.number_of_clients
        event = TimeTick(now, correlation_id)
        self.__sender(event)
