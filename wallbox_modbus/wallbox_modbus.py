from pymodbus.client import AsyncModbusTcpClient
from wallbox_modbus.constants import (
    Action,
    AutoChargingDischarging,
    Control,
    ChargerLockState,
    ChargerStates,
    RegisterAddresses,
    SetpointType,
)

class WallboxModbus:

    def __init__(self, host, port=502) -> None:
        self.host = host
        self.port = port
        self.client = AsyncModbusTcpClient(host=host, port=port)

    async def connect(self):
        return await self.client.connect()

    def close(self):
        self.client.close()

    async def _read(self, address, count=1):
        return await self.client.read_holding_registers(address, count, slave=1)

    async def _write(self, address, value):
        return await self.client.write_register(address, value, slave=1)

    ### Firmware version ###

    async def get_firmware_version(self):
        result = await self._read(RegisterAddresses.FIRMWARE_VERSION)
        return result.registers[0]

    ### Serial number ###

    async def get_serial_number(self):
        result = await self._read(RegisterAddresses.SERIAL_HIGH, 2)
        return to_serial_number(result.registers)

    ### Part number ###

    async def get_part_number(self):
        result = await self._read(RegisterAddresses.PART_NUMBER_1, 6)
        return to_part_number(result.registers)

    ### Control ###

    async def has_control(self):
        result = await self._read(RegisterAddresses.CONTROL)
        return result.registers[0] == Control.REMOTE

    async def release_control(self):
        await self._write(RegisterAddresses.CONTROL, Control.USER)

    async def take_control(self):
        await self._write(RegisterAddresses.CONTROL, Control.REMOTE)

    ### Auto charging/discharging ###

    async def is_auto_charging_discharging_enabled(self):
        result = await self._read(RegisterAddresses.AUTO_CHARGING_DISCHARGING)
        return result.registers[0] == AutoChargingDischarging.ENABLE

    async def disable_auto_charging_discharging(self):
        await self._write(RegisterAddresses.AUTO_CHARGING_DISCHARGING, AutoChargingDischarging.DISABLE)

    async def enable_auto_charging_discharging(self):
        await self._write(RegisterAddresses.AUTO_CHARGING_DISCHARGING, AutoChargingDischarging.ENABLE)

    ### Setpoint type ###

    async def get_setpoint_type(self):
        result = await self._read(RegisterAddresses.SETPOINT_TYPE)
        return result.registers[0]

    async def set_setpoint_type(self, setpoint_type):
        await self._write(RegisterAddresses.SETPOINT_TYPE, setpoint_type)

    ### Charger lock state ###

    async def is_charger_locked(self):
        result = await self._read(RegisterAddresses.CHARGER_LOCK_STATE)
        return result.registers[0] == ChargerLockState.LOCK

    async def lock_charger(self):
        await self._write(RegisterAddresses.CHARGER_LOCK_STATE, ChargerLockState.LOCK)

    async def unlock_charger(self):
        await self._write(RegisterAddresses.CHARGER_LOCK_STATE, ChargerLockState.UNLOCK)

    ### Action ###

    async def start_charging_discharging(self):
        await self._write(RegisterAddresses.ACTION, Action.START_CHARGING_DISCHARGING)

    async def stop_charging_discharging(self):
        await self._write(RegisterAddresses.ACTION, Action.STOP_CHARGING_DISCHARGING)

    async def reboot_charger(self):
        await self._write(RegisterAddresses.ACTION, Action.REBOOT_CHARGER)

    async def update_firmware(self):
        await self._write(RegisterAddresses.ACTION, Action.UPDATE_FIRMWARE)

    ### Current setpoint ###

    async def get_current_setpoint(self) -> int:
        result = await self._read(RegisterAddresses.CURRENT_SETPOINT)
        return uint16_to_int16(result.registers[0])

    async def set_current_setpoint(self, value: int):
        await self._write(RegisterAddresses.CURRENT_SETPOINT, int16_to_uint16(value))

    ### Power setpoint ###

    async def get_power_setpoint(self) -> int:
        result = await self._read(RegisterAddresses.POWER_SETPOINT)
        return uint16_to_int16(result.registers[0])

    async def set_power_setpoint(self, value: int):
        await self._write(RegisterAddresses.POWER_SETPOINT, int16_to_uint16(value))

    ### Max available current / power

    async def get_max_available_current(self) -> int:
        result = await self._read(RegisterAddresses.MAX_AVAILABLE_CURRENT)
        return result.registers[0]

    async def get_max_available_power(self) -> int:
        result = await self._read(RegisterAddresses.MAX_AVAILABLE_POWER)
        return result.registers[0]

    ### AC current / voltage / active power RMS

    async def get_ac_current_rms(self) -> int:
        result = await self._read(RegisterAddresses.AC_CURRENT_RMS)
        return result.registers[0]

    async def get_ac_voltage_rms(self) -> int:
        result = await self._read(RegisterAddresses.AC_VOLTAGE_RMS)
        return result.registers[0]

    async def get_ac_active_power_rms(self) -> int:
        result = await self._read(RegisterAddresses.AC_ACTIVE_POWER_RMS)
        return result.registers[0]

    ### Charger state ###

    async def is_car_connected(self) -> bool:
        result = await self._read(RegisterAddresses.CHARGER_STATE)
        return result.registers[0] != ChargerStates.NO_CAR_CONNECTED

    ### State of charge ###

    async def get_state_of_charge(self) -> int:
        result = await self._read(RegisterAddresses.STATE_OF_CHARGE)
        return result.registers[0]

    ### All ###

    async def get_all_values(self) -> dict:
        result0 = await self._read(RegisterAddresses.FIRMWARE_VERSION, 9)
        result1 = await self._read(RegisterAddresses.CONTROL, 3)
        result2 = await self._read(RegisterAddresses.CHARGER_LOCK_STATE, 5)
        result3 = await self._read(RegisterAddresses.MAX_AVAILABLE_CURRENT, 27)
        return {
            'firmware_version': result0.registers[0],
            'serial_number': to_serial_number(result0.registers[1:3]),
            'part_number': to_part_number(result0.registers[3:10]),

            'control': 'user' if result1.registers[0] == Control.USER else 'remote',
            'is_auto_charging_discharging_enabled': result1.registers[1] == AutoChargingDischarging.ENABLE,
            'setpoint_type': 'current' if result1.registers[2] == SetpointType.CURRENT else 'power',

            'is_charger_locked': result2.registers[0] == ChargerLockState.LOCK,
            'current_setpoint': uint16_to_int16(result2.registers[2]),
            'power_setpoint': uint16_to_int16(result2.registers[4]),

            'max_available_current': result3.registers[0],
            'max_available_power': result3.registers[2],
            'ac_current_rms': result3.registers[7],
            'ac_voltage_rms': result3.registers[10],
            'ac_active_power_rms': result3.registers[14],
            'charger_state': ChargerStates._value2member_map_[result3.registers[25]].name.lower(),
            'state_of_charge': result3.registers[26],
        }


def to_serial_number(values):
    return (values[0]<<16) + values[1]

def to_part_number(values):
    return (
        chr(0xff & (values[0]>>8)) + chr(0xff & values[0]) +
        chr(0xff & (values[1]>>8)) + chr(0xff & values[1]) + '-' +
        chr(0xff & (values[2]>>8)) + '-' + chr(0xff & values[2]) + '-' +
        chr(0xff & (values[3]>>8)) + '-' + chr(0xff & values[3]) + '-' +
        chr(0xff & (values[4]>>8)) + chr(0xff & values[4]) +
        chr(0xff & (values[5]>>8)) + '-' + chr(0xff & values[5])
    )


MAX_USI = 65536
HALF_MAX_USI = MAX_USI/2

def int16_to_uint16(value):
    if value < 0:
        value = value + MAX_USI
    return value

def uint16_to_int16(value):
    if value > HALF_MAX_USI:
        value = value - MAX_USI
    return value

