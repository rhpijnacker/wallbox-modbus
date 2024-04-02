import pytest
import pytest_asyncio
from pymodbus.transport import NULLMODEM_HOST
from wallbox_modbus import WallboxModbus
from wallbox_modbus.constants import ChargerStates, RegisterAddresses

pytestmark = pytest.mark.asyncio

class TestWallboxModbus:

    wallbox: WallboxModbus

    @pytest_asyncio.fixture(autouse=True)
    async def _setup_teardown(self):
        self.wallbox = WallboxModbus(NULLMODEM_HOST)
        yield
        self.wallbox.close()

    async def test_connect(self, fake_wallbox_modbus_server):
        # Act
        await self.wallbox.connect()
        # Assert
        assert len(fake_wallbox_modbus_server.active_connections) == 1

    async def test_car_is_connected(self, fake_wallbox_modbus_server):
        # Arrange
        mock_car_is_connected(fake_wallbox_modbus_server)
        await self.wallbox.connect()
        # Act
        is_connected = await self.wallbox.is_car_connected()
        # Assert
        assert is_connected

    async def test_car_is_not_connected(self, fake_wallbox_modbus_server):
        # Arrange
        mock_car_is_not_connected(fake_wallbox_modbus_server)
        await self.wallbox.connect()
        # Act
        is_connected = await self.wallbox.is_car_connected()
        # Assert
        assert not is_connected


def mock_car_is_not_connected(server):
    set_modbus_values(server, RegisterAddresses.CHARGER_STATE, [ChargerStates.NO_CAR_CONNECTED])

def mock_car_is_connected(server):
    set_modbus_values(server, RegisterAddresses.CHARGER_STATE, [ChargerStates.CONNECTED_NOT_CHARGING])

def set_modbus_values(server, start_address, values):
    fc_as_hex = 0x3
    slave_id = 0
    return server.context[slave_id].setValues(fc_as_hex, start_address, values)
 