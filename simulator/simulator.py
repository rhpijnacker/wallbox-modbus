#!../venv/bin/python3

import asyncio
import logging
from pymodbus import pymodbus_apply_logging_config
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.register_write_message import (
    WriteMultipleRegistersRequest,
    WriteSingleRegisterRequest,
)
from pymodbus.server import ModbusTcpServer

#pymodbus_apply_logging_config(logging.DEBUG)

class WallboxSimulator:

    server: ModbusTcpServer

    def __init__(self):
        # callback functions for handling writes to write registers
        self._write_handlers = {
            0x51:  self._handle_set_control,
            # 0x53:  self._handle_set_setpoint_type, -- ignore when user control?
            0x101: self._handle_set_action
        }

    async def setup(self):
        datablock = ModbusSequentialDataBlock(0x00, [0] * 547)
        context = ModbusSlaveContext(hr=datablock)
        self.context = ModbusServerContext(slaves=context, single=True)
        self.server = ModbusTcpServer(
            context=self.context, 
            address=('', 5020), 
            request_tracer=self._server_request_tracer,
        )
        self._set_modbus_values_initial()
        self._set_modbus_values_connected_idle()

    async def run(self):
        await self.server.serve_forever()

    def _set_modbus_values_initial(self):
        self._set_modbus_values(0x1, [
            3400, # 0x1: firmware version
            5,    # 0x2: s/n high
            19659 # 0x3: s/n low
        ])
        self._set_modbus_values(0x50, [
            5020, # 0x50: communication port (uint16  502, 1024-65535)
            1,    # 0x51: control (0: user* / 1: remote)
            0,    # 0x52: start charging on EV-Gun connected (0: disable / 1: enable)
            1,    # 0x53: setpoint type (0: current / 1: power by phase)
            0,    # 0x54: set setpoint on idle state (0: disable / 1: enable)
            6,    # 0x55: current setpoint on idle state (int16  -32A to 32)
            0,    # 0x56: reserved
            5750, # 0x57: power setpoint on idle state (int16  -7400W to 7400)
        ])

    def _set_modbus_values_control_user(self):
        self._set_modbus_values(0x52, [
            1,    # 0x52: start charging on EV-Gun connected (0: disable / 1: enable)
            0,    # 0x53: setpoint type (0: current / 1: power by phase)
            0,    # 0x54: set setpoint on idle state (0: disable / 1: enable)
            6,    # 0x55: current setpoint on idle state (int16  -32A to 32)
            0,    # 0x56: reserved
            0,    # 0x57: power setpoint on idle state (int16  -7400W to 7400)
        ])

    def _set_modbus_values_control_remote(self):
        # no values are automatically (re)set when control is set to remote
        pass

    def _set_modbus_values_connected_idle(self):
        self._set_modbus_values(0x100, [
            1,    # 0x100: charger lock state (0: unlock / 1: lock)
            0,    # 0x101: action (1: start (dis)charging / 2: stop (dis)charging / 3: reboot charger / 4: update firmware)
            25,   # 0x102: current setpoint (int16  -32A to 32)
            0,    # 0x103: reserved
            5750, # 0x104: power setpoint (int16  -7400W to 7400)
        ])
        self._set_modbus_values(0x200, [
            25,   # 0x200: max available current (uint16  0A to 32)
            0,    # 0x201: reserved
            5750, # 0x202: max available power (uint16  0W to 7400)
            0, 0, 0, 0, # 0x203-0x206: reserved
            25,   # 0x207: ac current rms L1 (uint16  0A to 100)
            0, 0, # 0x208-0x209: reserved
            230,  # 0x20a: ac voltage rms L1 (uint16  0V to 500)
            0, 0, 0, # 0x20b-0x20d: reserved
            0,    # 0x20e: ac active power rms L1 (uint16  0W to 50000)
        ])
        self._set_modbus_values(0x219, [
            4,    # 0x219: charger status (4: connected, paused by user)
            55,   # 0x21a: state of charge
        ])

    def _set_modbus_values_connected_charging(self):
        self._set_modbus_values(0x20e, [
            # what about 0x207 ac current?
            5750, # 0x20e: ac active power rms L1 (uint16  0W to 50000)
        ])
        self._set_modbus_values(0x219, [
            1,    # 0x219: charger status (1: charging)
            33,   # 0x21a: state of charge
        ])

    def _set_modbus_values(self, start_address, values):
        fc_as_hex = 0x3
        slave_id = 0
        self.context[slave_id].setValues(fc_as_hex, start_address, values)

    def _server_request_tracer(self, request, *_addr):
        print(f"---> REQUEST: {request}")
        if isinstance(request, WriteMultipleRegistersRequest):
            self._process_write_registers(request.address, request.values)
        if isinstance(request, WriteSingleRegisterRequest):
            self._process_write_registers(request.address, [request.value])

    def _process_write_registers(self, start_address, values):
        for address in range(start_address, start_address+len(values)):
            if address in self._write_handlers:
                cur = self._get_modbus_value(address)
                new = values[address-start_address]
                if cur != new:
                    self._write_handlers[address](address, new)

    def _get_modbus_value(self, address):
        fc_as_hex = 0x3
        slave_id = 0
        return self.context[slave_id].getValues(fc_as_hex, address)[0]

    def _handle_set_control(self, address, value):
        print(f"--> set control {address} -> {value}")
        if value == 0: # user
            self._set_modbus_values_control_user()
        elif value == 1: # remote
            self._set_modbus_values_control_remote()

    def _handle_set_action(self, address, value):
        print(f"--> set action {address} -> {value}")
        if value == 1: # start (dis)charging
            self._set_modbus_values_connected_charging()
        elif value == 2: # stop (dis)charging
            self._set_modbus_values_connected_idle()
       

async def main():
    simulator = WallboxSimulator()
    await simulator.setup()
    await simulator.run()

asyncio.run(main())