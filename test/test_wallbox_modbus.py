import pytest
import pytest_asyncio
from pymodbus.transport import NULLMODEM_HOST
from wallbox_modbus import WallboxModbus
from wallbox_modbus.wallbox_modbus import (
    int16_to_uint16,
    uint16_to_int16,
)
from wallbox_modbus.constants import (
    Action,
    AutoChargingDischarging,
    Control, 
    ChargerLockState,
    ChargerStates, 
    RegisterAddresses,
    SetpointType,
)

pytestmark = pytest.mark.asyncio

class TestWallboxModbus:

    wallbox: WallboxModbus

    @pytest_asyncio.fixture(autouse=True)
    async def _setup_teardown(self):
        self.wallbox = WallboxModbus(NULLMODEM_HOST)
        yield
        self.wallbox.close()

    @pytest_asyncio.fixture
    async def connect_to_wallbox(self):
        await self.wallbox.connect()


    async def test_connect(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Assert
        assert len(fake_wallbox_modbus_server.active_connections) == 1

    # Control

    async def test_release_control(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Act
        await self.wallbox.release_control()
        has_control = await self.wallbox.has_control()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.CONTROL) == Control.USER
        assert not has_control

    async def test_take_control(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Act
        await self.wallbox.take_control()
        has_control = await self.wallbox.has_control()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.CONTROL) == Control.REMOTE
        assert has_control

    # Start charging/discharging on EV-Gun conected

    async def test_disable_auto_charging_discharging(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Arrange
        set_server_values(fake_wallbox_modbus_server, RegisterAddresses.AUTO_CHARGING_DISCHARGING, [AutoChargingDischarging.ENABLE])
        is_enabled = await self.wallbox.is_auto_charging_discharging_enabled()
        assert is_enabled
        # Act
        await self.wallbox.disable_auto_charging_discharging()
        is_enabled = await self.wallbox.is_auto_charging_discharging_enabled()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.AUTO_CHARGING_DISCHARGING) == AutoChargingDischarging.DISABLE
        assert not is_enabled

    async def test_disable_auto_charging_discharging(self, fake_wallbox_modbus_server, connect_to_wallbox):
        is_enabled = await self.wallbox.is_auto_charging_discharging_enabled()
        assert not is_enabled
        # Act
        await self.wallbox.enable_auto_charging_discharging()
        is_enabled = await self.wallbox.is_auto_charging_discharging_enabled()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.AUTO_CHARGING_DISCHARGING) == AutoChargingDischarging.ENABLE
        assert is_enabled

    # Setpoint type
        
    async def test_set_setpoint_type(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Arrange
        type = await self.wallbox.get_setpoint_type()
        assert type == SetpointType.CURRENT
        # Act
        await self.wallbox.set_setpoint_type(SetpointType.POWER)
        type = await self.wallbox.get_setpoint_type()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.SETPOINT_TYPE) == SetpointType.POWER
        assert type == SetpointType.POWER

    # Charger lock state
        
    async def test_lock_charger(self, fake_wallbox_modbus_server, connect_to_wallbox):
        is_locked = await self.wallbox.is_charger_locked()
        assert not is_locked
        # Act
        await self.wallbox.lock_charger()
        is_locked = await self.wallbox.is_charger_locked()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.CHARGER_LOCK_STATE) == ChargerLockState.LOCK
        assert is_locked

    async def test_unlock_charger(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Arrange
        set_server_values(fake_wallbox_modbus_server, RegisterAddresses.CHARGER_LOCK_STATE, [ChargerLockState.LOCK])
        is_locked = await self.wallbox.is_charger_locked()
        assert is_locked
        # Act
        await self.wallbox.unlock_charger()
        is_locked = await self.wallbox.is_charger_locked()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.CHARGER_LOCK_STATE) == ChargerLockState.UNLOCK
        assert not is_locked

    # Action
        
    async def test_start_charging_discharging(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Act
        await self.wallbox.start_charging_discharging()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.ACTION) == Action.START_CHARGING_DISCHARGING

    async def test_stop_charging_discharging(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Act
        await self.wallbox.stop_charging_discharging()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.ACTION) == Action.STOP_CHARGING_DISCHARGING

    async def test_reboot_charger(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Act
        await self.wallbox.reboot_charger()
        # Assert
        # For a real server this does not make sense ...
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.ACTION) == Action.REBOOT_CHARGER

    async def test_update_firmware(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Act
        await self.wallbox.update_firmware()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.ACTION) == Action.UPDATE_FIRMWARE

    # Current setpoint

    async def test_positive_current_setpoint(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Act
        await self.wallbox.set_current_setpoint(23)
        value = await self.wallbox.get_current_setpoint()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.CURRENT_SETPOINT) == 23
        assert value == 23

    async def test_negative_current_setpoint(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Act
        await self.wallbox.set_current_setpoint(-23)
        value = await self.wallbox.get_current_setpoint()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.CURRENT_SETPOINT) == 65536 - 23
        assert value == -23

    # Power setpoint

    async def test_positive_power_setpoint(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Act
        await self.wallbox.set_power_setpoint(2345)
        value = await self.wallbox.get_power_setpoint()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.POWER_SETPOINT) == 2345
        assert value == 2345

    async def test_negative_power_setpoint(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Act
        await self.wallbox.set_power_setpoint(-2345)
        value = await self.wallbox.get_power_setpoint()
        # Assert
        assert get_server_value(fake_wallbox_modbus_server, RegisterAddresses.POWER_SETPOINT) == 65536 - 2345
        assert value == -2345

    # Max available current / power

    async def test_get_max_available_current(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Arrange
        set_server_values(fake_wallbox_modbus_server, RegisterAddresses.MAX_AVAILABLE_CURRENT, [23])
        # Act
        value = await self.wallbox.get_max_available_current()
        # Assert
        assert value == 23

    async def test_get_max_available_power(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Arrange
        set_server_values(fake_wallbox_modbus_server, RegisterAddresses.MAX_AVAILABLE_POWER, [2345])
        # Act
        value = await self.wallbox.get_max_available_power()
        # Assert
        assert value == 2345

    # AC current / voltage / active power RMS

    async def test_get_ac_current_rms(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Arrange
        set_server_values(fake_wallbox_modbus_server, RegisterAddresses.AC_CURRENT_RMS, [23])
        # Act
        value = await self.wallbox.get_ac_current_rms()
        # Assert
        assert value == 23

    async def test_get_ac_voltage_rms(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Arrange
        set_server_values(fake_wallbox_modbus_server, RegisterAddresses.AC_VOLTAGE_RMS, [234])
        # Act
        value = await self.wallbox.get_ac_voltage_rms()
        # Assert
        assert value == 234

    async def test_get_ac_active_power_rms(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Arrange
        set_server_values(fake_wallbox_modbus_server, RegisterAddresses.AC_ACTIVE_POWER_RMS, [2345])
        # Act
        value = await self.wallbox.get_ac_active_power_rms()
        # Assert
        assert value == 2345

    # Charger state

    async def test_car_is_connected(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Arrange
        mock_car_is_connected(fake_wallbox_modbus_server)
        # Act
        is_connected = await self.wallbox.is_car_connected()
        # Assert
        assert is_connected

    async def test_car_is_not_connected(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Arrange
        mock_car_is_not_connected(fake_wallbox_modbus_server)
        # Act
        is_connected = await self.wallbox.is_car_connected()
        # Assert
        assert not is_connected

    # State of charge

    async def test_get_state_of_charge(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Arrange
        set_server_values(fake_wallbox_modbus_server, RegisterAddresses.STATE_OF_CHARGE, [23])
        # Act
        value = await self.wallbox.get_state_of_charge()
        # Assert
        assert value == 23

    # All data

    async def test_get_all_values(self, fake_wallbox_modbus_server, connect_to_wallbox):
        # Arrange
        set_server_values(fake_wallbox_modbus_server, RegisterAddresses.CONTROL, [
            Control.REMOTE,
            AutoChargingDischarging.ENABLE,
            SetpointType.POWER,
        ])
        set_server_values(fake_wallbox_modbus_server, RegisterAddresses.CHARGER_LOCK_STATE, [
            ChargerLockState.LOCK,
            0, # Action - ignored
            int16_to_uint16(-23), # current setpoint
            0, # reserved
            int16_to_uint16(-2345), # power setpoint
        ])
        set_server_values(fake_wallbox_modbus_server, RegisterAddresses.MAX_AVAILABLE_CURRENT, [
            23, # max available current
            0, # reserved,
            2345, # max available power
            0, 0, 0, 0, # reserved
            23, # ac current rms
            0, 0, # reserved
            234, # ac voltage rms
            0, 0, 0, # reserved
            2345, # ac active power rms
        ])
        set_server_values(fake_wallbox_modbus_server, RegisterAddresses.CHARGER_STATE, [
            ChargerStates.DISCHARGING,
            23, # state of charge
        ])
        # Act
        data = await self.wallbox.get_all_values()
        # Assert
        assert data.get('control') == 'remote'
        assert data.get('is_auto_charging_discharging_enabled') == True
        assert data.get('setpoint_type') == 'power'
        assert data.get('is_charger_locked') == True
        assert data.get('current_setpoint') == -23
        assert data.get('power_setpoint') == -2345
        assert data.get('max_available_current') == 23
        assert data.get('max_available_power') == 2345
        assert data.get('ac_current_rms') == 23
        assert data.get('ac_voltage_rms') == 234
        assert data.get('ac_active_power_rms') == 2345
        assert data.get('charger_state') == 'discharging'
        assert data.get('state_of_charge') == 23


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
