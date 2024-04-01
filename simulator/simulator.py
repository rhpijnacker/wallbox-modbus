import asyncio
from pymodbus.datastore import ModbusSimulatorContext
from pymodbus.server import ModbusSimulatorServer
import os

cwd = os.path.dirname(os.path.abspath(__file__))

async def main():
    server = ModbusSimulatorServer(
        modbus_server='server',
        modbus_device='Wallbox EVSE',
        http_host='0.0.0.0',
        http_port=8080,
        log_file=f'{cwd}/simulator.log',
        json_file=f'{cwd}/configuration.json',
    )
    await server.run_forever()

asyncio.run(main())