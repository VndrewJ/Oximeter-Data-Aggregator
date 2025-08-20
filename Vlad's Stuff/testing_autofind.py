from bleak import BleakScanner
from bleak import BleakClient
import asyncio


DEVICE_ADDRESS = ""
CHAR_UUID = ""

# Global variables to accumulate values
spo2_sum = 0
hr_sum = 0
count = 0

async def find_device():
    global DEVICE_ADDRESS, CHAR_UUID

    devices = await BleakScanner.discover()

    for d in devices:
        if d.name == "BLT_M70C":  # Replace with your device name
            print(f"Found device: {d.name} - {d.address}")
            DEVICE_ADDRESS = d.address
            break
    
    if not DEVICE_ADDRESS:
        return -1
    
    async with BleakClient(DEVICE_ADDRESS) as client:
        # connection automatically discovers services
        services = client.services

        # Pick the first notify-able characteristic
        for service in services:
            for char in service.characteristics:
                if "notify" in char.properties:
                    return char.uuid
    
    return -1


def notification_handler(sender, data):
    global spo2_sum, hr_sum, count

    print(f"{list(data)}")


async def main():
    global DEVICE_ADDRESS, CHAR_UUID   

    CHAR_UUID = await find_device()

    if CHAR_UUID == -1:
        print("Device not found.")
        return
    
    print(f"Using characteristic: {CHAR_UUID}")

    async with BleakClient(DEVICE_ADDRESS) as client:
        print("Connected. Subscribing to notifications...")
        await client.start_notify(CHAR_UUID, notification_handler)
        await asyncio.sleep(10)  # Listen for 30 seconds
        await client.stop_notify(CHAR_UUID)
        print("Stopped.")

asyncio.run(main())
