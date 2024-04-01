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

    async def test_car_connected(self, fake_wallbox_modbus_server):
        # Arrange
        mock_car_is_connected(fake_wallbox_modbus_server)
        await self.wallbox.connect()
        # Act
        is_connected = await self.wallbox.is_car_connected()
        # Assert
        assert is_connected


def mock_car_is_connected(server):
    store = get_datastore(server)
    store.setValues(RegisterAddresses.CHARGER_STATE, [ChargerStates.CONNECTED_NOT_CHARGING])

def get_datastore(server):
    return server.context[0].store['h']