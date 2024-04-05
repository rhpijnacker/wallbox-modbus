from pymodbus.client import AsyncModbusTcpClient
from wallbox_modbus.constants import (
    Action,
    AutoChargingDischarging,
    Control, 
    ChargerLockState,
    ChargerStates, 
    RegisterAddresses, 
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

    ### Control ###

    async def has_control(self):
        result = await self.client.read_holding_registers(RegisterAddresses.CONTROL)
        return result.registers[0] == Control.REMOTE

    async def release_control(self):
        await self.client.write_register(RegisterAddresses.CONTROL, Control.USER)

    async def take_control(self):
        await self.client.write_register(RegisterAddresses.CONTROL, Control.REMOTE)

    ### Auto charging/discharging ###

    async def is_auto_charging_discharging_enabled(self):
        result = await self.client.read_holding_registers(RegisterAddresses.AUTO_CHARGING_DISCHARGING)
        return result.registers[0] == AutoChargingDischarging.ENABLE

    async def disable_auto_charging_discharging(self):
        await self.client.write_register(RegisterAddresses.AUTO_CHARGING_DISCHARGING, AutoChargingDischarging.DISABLE)

    async def enable_auto_charging_discharging(self):
        await self.client.write_register(RegisterAddresses.AUTO_CHARGING_DISCHARGING, AutoChargingDischarging.ENABLE)

    ### Setpoint type ###
        
    async def get_setpoint_type(self):
        result = await self.client.read_holding_registers(RegisterAddresses.SETPOINT_TYPE)
        return result.registers[0]

    async def set_setpoint_type(self, setpoint_type):
        await self.client.write_register(RegisterAddresses.SETPOINT_TYPE, setpoint_type)

    ### Charger lock state ###
        
    async def is_charger_locked(self):
        result = await self.client.read_holding_registers(RegisterAddresses.CHARGER_LOCK_STATE)
        return result.registers[0] == ChargerLockState.LOCK

    async def lock_charger(self):
        await self.client.write_register(RegisterAddresses.CHARGER_LOCK_STATE, ChargerLockState.LOCK)

    async def unlock_charger(self):
        await self.client.write_register(RegisterAddresses.CHARGER_LOCK_STATE, ChargerLockState.UNLOCK)

    ### Action ###
        
    async def start_charging_discharging(self):
        await self.client.write_register(RegisterAddresses.ACTION, Action.START_CHARGING_DISCHARGING)

    async def stop_charging_discharging(self):
        await self.client.write_register(RegisterAddresses.ACTION, Action.STOP_CHARGING_DISCHARGING)

    async def reboot_charger(self):
        await self.client.write_register(RegisterAddresses.ACTION, Action.REBOOT_CHARGER)

    async def update_firmware(self):
        await self.client.write_register(RegisterAddresses.ACTION, Action.UPDATE_FIRMWARE)

    ### Current setpoint ###

    async def get_current_setpoint(self):
        result = await self.client.read_holding_registers(RegisterAddresses.CURRENT_SETPOINT)
        return uint16_to_int16(result.registers[0])

    async def set_current_setpoint(self, value: int):
        await self.client.write_register(RegisterAddresses.CURRENT_SETPOINT, int16_to_uint16(value))

    ### Power setpoint ###

    async def get_power_setpoint(self):
        result = await self.client.read_holding_registers(RegisterAddresses.POWER_SETPOINT)
        return uint16_to_int16(result.registers[0])

    async def set_power_setpoint(self, value: int):
        await self.client.write_register(RegisterAddresses.POWER_SETPOINT, int16_to_uint16(value))

    ### Charger state ###

    async def is_car_connected(self) -> bool:
        result = await self.client.read_holding_registers(RegisterAddresses.CHARGER_STATE)
        return result.registers[0] != ChargerStates.NO_CAR_CONNECTED


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

