import asyncio
import pytest
import pytest_asyncio
from pymodbus import pymodbus_apply_logging_config
from pymodbus.datastore import ModbusServerContext
from pymodbus.server import ModbusTcpServer
from pymodbus.transport import NULLMODEM_HOST

#pymodbus_apply_logging_config("DEBUG")

@pytest.fixture
def context():
    return ModbusServerContext()

@pytest_asyncio.fixture
async def fake_wallbox_modbus_server(context):
    server = ModbusTcpServer(context=context, address=(NULLMODEM_HOST, 502))
    asyncio.create_task(server.serve_forever())
    yield server
    await server.shutdown()
