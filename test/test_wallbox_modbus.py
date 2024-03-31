import pytest
from pymodbus.transport import NULLMODEM_HOST
from wallbox_modbus import WallboxModbus

class TestWallboxModbus:

    @pytest.mark.asyncio
    async def test_connect(self, fake_wallbox_modbus_server):
        # Arrange
        wallbox = WallboxModbus(NULLMODEM_HOST)
        # Act
        await wallbox.connect()
        # Assert
        assert len(fake_wallbox_modbus_server.active_connections) == 1
        # Cleanup
        wallbox.close()