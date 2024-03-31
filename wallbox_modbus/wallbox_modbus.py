from pymodbus.client import AsyncModbusTcpClient

class WallboxModbus:

    def __init__(self, host, port=502) -> None:
        self.host = host
        self.port = port
        self.client = AsyncModbusTcpClient(host=host, port=port)

    async def connect(self):
        return await self.client.connect()

    def close(self):
        self.client.close()