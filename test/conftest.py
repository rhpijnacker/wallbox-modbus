import asyncio
import pytest
import pytest_asyncio
from pymodbus import pymodbus_apply_logging_config
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext, ModbusSequentialDataBlock
from pymodbus.server import ModbusTcpServer
from pymodbus.transport import NULLMODEM_HOST
from wallbox_modbus.constants import ChargerStates, RegisterAddresses

#pymodbus_apply_logging_config("DEBUG")

@pytest.fixture
def datablock():
    datablock = ModbusSequentialDataBlock(0x00, [0] * 547)
    return datablock

@pytest.fixture
def context(datablock):
    slave_context = ModbusSlaveContext(hr=datablock)
    return ModbusServerContext(slaves=slave_context, single=True)

@pytest_asyncio.fixture
async def fake_wallbox_modbus_server(context):
    server = ModbusTcpServer(context=context, address=(NULLMODEM_HOST, 502))
    asyncio.create_task(server.serve_forever())
    yield server
    await server.shutdown()
