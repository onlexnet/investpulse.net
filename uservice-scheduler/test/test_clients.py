from statistics import correlation
from typing import Optional, cast
from unittest import TestCase
from datetime import datetime
import unittest
import pytest
from src.clients import ClientsHub
import scheduler_rpc.schema_pb2 as proto

from src.mapper import to_dto

@pytest.mark.asyncio
async def test_aaa():
    pass

class KnownClientsTest(unittest.IsolatedAsyncioTestCase):

    @pytest.mark.asyncio
    async def test_emit_first_event(self):

        maybe_handled: Optional[proto.NewTime] = None
        async def client(event: proto.NewTime):
            nonlocal maybe_handled
            maybe_handled = event

        now = datetime(2001, 1, 1)
        sut = ClientsHub(1, now, now)
        await sut.add_client(client)

        handled = cast(proto.NewTime, maybe_handled)
        correlation_id = handled.correlationId

        self.assertIsInstance(handled, proto.NewTime)
        expected = to_dto(now, correlation_id)
        self.assertEqual(handled, expected)


    @pytest.mark.asyncio
    # @pytest.mark.skip
    async def test_emit_final_event(self):

        maybe_handled: Optional[proto.NewTime] = None
        async def client(event: proto.NewTime):
            nonlocal maybe_handled
            maybe_handled = event

        sut = ClientsHub(1, datetime(2001, 1, 1), datetime(2001, 1, 1, 0, 1))
        await sut.add_client(client)

        correlation_id1 = cast(proto.NewTime, maybe_handled).correlationId
        await sut.on_client_ack(correlation_id1)

        correlation_id2 = cast(proto.NewTime, maybe_handled).correlationId

        self.assertIsInstance(maybe_handled, proto.NewTime)
        self.assertEqual(maybe_handled, proto.NewTime(correlationId=correlation_id2, yyyymmdd = 20010101, hhmm=1))