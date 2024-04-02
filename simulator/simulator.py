#!../venv/bin/python3

import asyncio
import logging
from pymodbus import pymodbus_apply_logging_config
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.server import ModbusTcpServer

pymodbus_apply_logging_config(logging.DEBUG)

class WallboxSimulator:

    server: ModbusTcpServer

    async def setup(self):
        datablock = ModbusSequentialDataBlock(0x00, [17] * 100)
        context = ModbusSlaveContext(di=datablock, co=datablock, hr=datablock, ir=datablock)
        context = ModbusServerContext(slaves=context, single=True)
        self.server = ModbusTcpServer(
            context=context, 
            address=('', 5021), 
            request_tracer=self.server_request_tracer,
            response_manipulator=self.server_response_manipulator,
        )

    def server_request_tracer(self, request, *_addr):
        print(f"---> REQUEST: {request}")

    def server_response_manipulator(self, response):
        print(f"---> RESPONSE: {response}")
        return response, False

    async def run(self):
        await self.server.serve_forever()

async def main():
    simulator = WallboxSimulator()
    await simulator.setup()
    await simulator.run()

asyncio.run(main())