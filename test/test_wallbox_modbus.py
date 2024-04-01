import pytest
from pymodbus.transport import NULLMODEM_HOST
from wallbox_modbus import WallboxModbus
from wallbox_modbus.constants import ChargerStates, RegisterAddresses

pytestmark = pytest.mark.asyncio

class TestWallboxModbus:

    async def test_connect(self, fake_wallbox_modbus_server):
        # Arrange
        wallbox = WallboxModbus(NULLMODEM_HOST)
        # Act
        await wallbox.connect()
        # Assert
        assert len(fake_wallbox_modbus_server.active_connections) == 1
        # Cleanup
        wallbox.close()

    async def test_car_connected(self, fake_wallbox_modbus_server):
        # Arrange
        mock_car_is_connected(fake_wallbox_modbus_server)
        wallbox = WallboxModbus(NULLMODEM_HOST)
        await wallbox.connect()
        # Act
        is_connected = await wallbox.is_car_connected()
        # Assert
        assert is_connected
        # Cleanup
        wallbox.close()


def mock_car_is_connected(server):
    store = get_datastore(server)
    store.setValues(RegisterAddresses.CHARGER_STATE, [ChargerStates.CONNECTED_NOT_CHARGING])

def get_datastore(server):
    return server.context[0].store['h']