#!../venv/bin/python3

from pymodbus import pymodbus_apply_logging_config
from pymodbus.client import ModbusTcpClient

#pymodbus_apply_logging_config("DEBUG")

client = ModbusTcpClient(host='localhost', port=5020)
client.connect()
result =  client.read_holding_registers(0x101, 2)
print('result', result.registers)

result = client.write_register(0x101, 1)

result =  client.read_holding_registers(0x219, 2)
print('result', result.registers)

result = client.write_registers(0x101, [2])

result =  client.read_holding_registers(0x219, 2)
print('result', result.registers)

client.close()
