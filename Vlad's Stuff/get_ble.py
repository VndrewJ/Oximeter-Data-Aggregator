from bleak import BleakClient
import asyncio

DEVICE_ADDRESS = "6C:79:B8:D5:1D:30"  # Your oximeter's MAC address

async def read_characteristics():
    async with BleakClient(DEVICE_ADDRESS) as client:
        # Services are discovered automatically after connection
        for service in client.services:
            print(f"Service: {service.uuid}")
            for char in service.characteristics:
                print(f"  Characteristic: {char.uuid}, Properties: {char.properties}")

asyncio.run(read_characteristics())
