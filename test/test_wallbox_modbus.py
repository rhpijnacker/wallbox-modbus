import pytest
import pytest_asyncio
from pymodbus.transport import NULLMODEM_HOST
from wallbox_modbus import WallboxModbus
from wallbox_modbus.constants import (
    Action,
    AutoChargingDischarging,
    Control, 
    ChargerLockState,
    ChargerStates, 
    RegisterAddresses,
    SetpointType
)

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

    # Control

    async def test_release_control(self, fake_wallbox_modbus_server):
        # Arrange
        await self.wallbox.connect()
        # Act
        await self.wallbox.release_control()
        has_control = await self.wallbox.has_control()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.CONTROL) == Control.USER
        assert not has_control

    async def test_take_control(self, fake_wallbox_modbus_server):
        # Arrange
        await self.wallbox.connect()
        # Act
        await self.wallbox.take_control()
        has_control = await self.wallbox.has_control()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.CONTROL) == Control.REMOTE
        assert has_control

    # Start charging/discharging on EV-Gun conected

    async def test_disable_auto_charging_discharging(self, fake_wallbox_modbus_server):
        # Arrange
        set_server_values(fake_wallbox_modbus_server, RegisterAddresses.AUTO_CHARGING_DISCHARGING, [AutoChargingDischarging.ENABLE])
        await self.wallbox.connect()
        is_enabled = await self.wallbox.is_auto_charging_discharging_enabled()
        assert is_enabled
        # Act
        await self.wallbox.disable_auto_charging_discharging()
        is_enabled = await self.wallbox.is_auto_charging_discharging_enabled()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.AUTO_CHARGING_DISCHARGING) == AutoChargingDischarging.DISABLE
        assert not is_enabled

    async def test_disable_auto_charging_discharging(self, fake_wallbox_modbus_server):
        # Arrange
        await self.wallbox.connect()
        is_enabled = await self.wallbox.is_auto_charging_discharging_enabled()
        assert not is_enabled
        # Act
        await self.wallbox.enable_auto_charging_discharging()
        is_enabled = await self.wallbox.is_auto_charging_discharging_enabled()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.AUTO_CHARGING_DISCHARGING) == AutoChargingDischarging.ENABLE
        assert is_enabled

    # Setpoint type
        
    async def test_set_setpoint_type(self, fake_wallbox_modbus_server):
        # Arrange
        await self.wallbox.connect()
        type = await self.wallbox.get_setpoint_type()
        assert type == SetpointType.CURRENT
        # Act
        await self.wallbox.set_setpoint_type(SetpointType.POWER)
        type = await self.wallbox.get_setpoint_type()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.SETPOINT_TYPE) == SetpointType.POWER
        assert type == SetpointType.POWER

    # Charger lock state
        
    async def test_lock_charger(self, fake_wallbox_modbus_server):
        # Arrange
        await self.wallbox.connect()
        is_locked = await self.wallbox.is_charger_locked()
        assert not is_locked
        # Act
        await self.wallbox.lock_charger()
        is_locked = await self.wallbox.is_charger_locked()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.CHARGER_LOCK_STATE) == ChargerLockState.LOCK
        assert is_locked

    async def test_unlock_charger(self, fake_wallbox_modbus_server):
        # Arrange
        set_server_values(fake_wallbox_modbus_server, RegisterAddresses.CHARGER_LOCK_STATE, [ChargerLockState.LOCK])
        await self.wallbox.connect()
        is_locked = await self.wallbox.is_charger_locked()
        assert is_locked
        # Act
        await self.wallbox.unlock_charger()
        is_locked = await self.wallbox.is_charger_locked()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.CHARGER_LOCK_STATE) == ChargerLockState.UNLOCK
        assert not is_locked

    # Action
        
    async def test_start_charging_discharging(self, fake_wallbox_modbus_server):
        # Arrange
        await self.wallbox.connect()
        # Act
        await self.wallbox.start_charging_discharging()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.ACTION) == Action.START_CHARGING_DISCHARGING

    async def test_stop_charging_discharging(self, fake_wallbox_modbus_server):
        # Arrange
        await self.wallbox.connect()
        # Act
        await self.wallbox.stop_charging_discharging()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.ACTION) == Action.STOP_CHARGING_DISCHARGING

    async def test_reboot_charger(self, fake_wallbox_modbus_server):
        # Arrange
        await self.wallbox.connect()
        # Act
        await self.wallbox.reboot_charger()
        # Assert
        # For a real server this does not make sense ...
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.ACTION) == Action.REBOOT_CHARGER

    async def test_update_firmware(self, fake_wallbox_modbus_server):
        # Arrange
        await self.wallbox.connect()
        # Act
        await self.wallbox.update_firmware()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.ACTION) == Action.UPDATE_FIRMWARE

    # Charger state

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
    set_server_values(server, RegisterAddresses.CHARGER_STATE, [ChargerStates.NO_CAR_CONNECTED])

def mock_car_is_connected(server):
    set_server_values(server, RegisterAddresses.CHARGER_STATE, [ChargerStates.CONNECTED_NOT_CHARGING])

def set_server_values(server, start_address, values):
    fc_as_hex = 0x3
    slave_id = 0
    return server.context[slave_id].setValues(fc_as_hex, start_address, values)

def get_server_value(server, address):
    fc_as_hex = 0x3
    slave_id = 0
    return server.context[slave_id].getValues(fc_as_hex, address)[0]
