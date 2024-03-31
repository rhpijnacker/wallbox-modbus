import asyncio
import pytest
from pymodbus.transport import NULLMODEM_HOST
from wallbox_modbus import WallboxModbus



class TestWallboxModbus:

    @pytest.mark.asyncio
    async def test_new(self):
        wallbox = WallboxModbus(NULLMODEM_HOST)

    @pytest.mark.asyncio
    async def test_connect(self):
        wallbox = WallboxModbus(NULLMODEM_HOST)
        await wallbox.connect()