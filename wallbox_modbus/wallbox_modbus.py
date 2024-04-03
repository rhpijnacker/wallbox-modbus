from pymodbus.client import AsyncModbusTcpClient
from wallbox_modbus.constants import (
    Control, 
    ChargerStates, 
    RegisterAddresses, 
    SetpointType
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

    ### Setpoint type ###
        
    async def get_setpoint_type(self):
        result = await self.client.read_holding_registers(RegisterAddresses.SETPOINT_TYPE)
        return result.registers[0]

    async def set_setpoint_type(self, setpoint_type):
        await self.client.write_register(RegisterAddresses.SETPOINT_TYPE, setpoint_type)

    ### Charger state ###

    async def is_car_connected(self) -> bool:
        result = await self.client.read_holding_registers(RegisterAddresses.CHARGER_STATE)
        return result.registers[0] != ChargerStates.NO_CAR_CONNECTED