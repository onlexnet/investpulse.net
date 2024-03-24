from statistics import correlation
from typing import Optional, cast
from unittest import TestCase
from datetime import datetime
import unittest
import pytest
from src.clients import ClientsHub, TimeTick
import scheduler_rpc.schema_pb2 as proto


from src.mapper import to_dto

class KnownClientsTest(unittest.IsolatedAsyncioTestCase):

    @pytest.mark.asyncio
    async def test_emit_first_event(self):

        maybe_handled: Optional[TimeTick] = None
        async def sender(event: TimeTick):
            nonlocal maybe_handled
            maybe_handled = event

        now = datetime(2001, 1, 1)
        sut = ClientsHub(1, now, now, sender)
        await sut.add_client()

        handled = cast(TimeTick, maybe_handled)
        correlation_id = handled.correlation_id

        self.assertIsInstance(handled, TimeTick)
        expected = TimeTick(now, correlation_id)
        self.assertEqual(handled, expected)


    @pytest.mark.asyncio
    async def test_emit_final_event(self):

        maybe_handled: Optional[TimeTick] = None
        async def client(event: TimeTick):
            nonlocal maybe_handled
            maybe_handled = event

        sut = ClientsHub(1, datetime(2001, 1, 1), datetime(2001, 1, 1, 0, 1), client)
        await sut.add_client()

        correlation_id1 = cast(TimeTick, maybe_handled).correlation_id
        await sut.on_client_ack(correlation_id1)

        handled2 = cast(TimeTick, maybe_handled)
        correlation_id2 = handled2.correlation_id
        now2 = handled2.now

        self.assertIsInstance(maybe_handled, TimeTick)
        self.assertEqual(maybe_handled, TimeTick(now2, correlation_id2))