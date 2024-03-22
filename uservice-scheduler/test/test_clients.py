from statistics import correlation
from typing import Optional, cast
from unittest import TestCase
import unittest
import pytest
from src.clients import ClientsHub, DateTime
import scheduler_rpc.schema_pb2 as proto

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

        now = DateTime(yyyymmdd = 20010101, hhmm=0)
        sut = ClientsHub(1, now, now)
        await sut.add_client(client)

        handled = cast(proto.NewTime, maybe_handled)
        correlation_id = handled.correlationId

        self.assertIsInstance(handled, proto.NewTime)
        self.assertEqual(handled, proto.NewTime(correlationId=correlation_id, yyyymmdd = now.yyyymmdd, hhmm=now.hhmm))


    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_emit_final_event(self):

        maybe_handled: Optional[proto.NewTime] = None
        async def client(event: proto.NewTime):
            nonlocal maybe_handled
            maybe_handled = event

        sut = ClientsHub(1, DateTime(yyyymmdd = 20010101, hhmm=0), DateTime(yyyymmdd = 20010101, hhmm=1))
        await sut.add_client(client)

        handled = cast(proto.NewTime, maybe_handled)
        correlation_id = handled.correlationId
        await sut.on_client_ack(correlation_id)

        self.assertIsInstance(maybe_handled, proto.NewTime)
        self.assertEqual(maybe_handled, proto.NewTime(correlationId=correlation_id, yyyymmdd = 20010101, hhmm=1))