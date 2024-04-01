import asyncio
import pytest
import pytest_asyncio
from pymodbus import pymodbus_apply_logging_config
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext, ModbusSparseDataBlock
from pymodbus.server import ModbusTcpServer
from pymodbus.transport import NULLMODEM_HOST
from wallbox_modbus.constants import ChargerStates, RegisterAddresses

pymodbus_apply_logging_config("DEBUG")

@pytest.fixture
def datablock():
     # data in the datablock is address one-off compared to addresses requested by the external API
     datablock = ModbusSparseDataBlock({RegisterAddresses.CHARGER_STATE+1: [12]}, mutable=True)
     return datablock

@pytest.fixture
def context(datablock):
    slave_context = ModbusSlaveContext(co=datablock, di=datablock, hr=datablock, ir=datablock)
    return ModbusServerContext(slaves=slave_context, single=True)

@pytest_asyncio.fixture
async def fake_wallbox_modbus_server(context):
    server = ModbusTcpServer(context=context, address=(NULLMODEM_HOST, 502))
    asyncio.create_task(server.serve_forever())
    yield server
    await server.shutdown()
