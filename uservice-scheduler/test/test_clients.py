from typing import Optional
from unittest import TestCase
import unittest
import pytest
from src.clients import ClientsHub
import scheduler_rpc.schema_pb2 as proto

@pytest.mark.asyncio
async def test_aaa():
    pass

class KnownClientsTest(unittest.IsolatedAsyncioTestCase):

    @pytest.mark.asyncio
    async def test_new_time_emit(self):

        handled: Optional[proto.NewTime] = None
        def client(event: proto.NewTime):
            nonlocal handled
            handled = event

        sut = ClientsHub(1, proto.NewTime(yyyymmdd = 20010101, hhmm=0000))
        await sut.add_client(client)

        self.assertIsInstance(handled, proto.NewTime)
        self.assertEqual(handled, proto.NewTime(yyyymmdd = 20010101, hhmm=0000))