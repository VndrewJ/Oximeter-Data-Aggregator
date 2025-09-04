from bleak import BleakScanner, BleakClient
import asyncio
import csv
import time
import os

DEVICE_ADDRESS = ""
CHAR_UUID = ""
Write_Interval = 5  # seconds
# Write_Duration = 60  # How long the program runs for before halting

# Store the latest data
latest_data = {"hr": None, "spo2": None, "timestamp": None}

# Buffer for current interval
data_buffer = []

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
        services = client.services
        for service in services:
            for char in service.characteristics:
                if "notify" in char.properties:
                    return char.uuid

    return -1


def notification_handler(sender, data: bytearray):
    """Parse HR and SpO₂ from raw data frame."""
    global latest_data
    raw = list(data)

    # Need at least 19 bytes if we are going to look at index 18
    if len(raw) < 19:
        return

    try:
        if raw[18] == 255 and not (raw[15] == 255 and raw[16] == 127 and raw[17] == 255):
            spo2 = raw[16]
            hr = raw[17]
            ts = int(time.time())
            data_buffer.append([ts, spo2, hr])
            print(f"Decoded -> HR={hr}, SpO₂={spo2}")
    except Exception as e:
        print("Parse error:", e)



async def csv_writer():
    """Background task to write and reset buffer every interval."""
    global data_buffer

    # Get absolute path to backend/data/oximeter_test_data.csv relative to script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_data_dir = os.path.abspath(os.path.join(base_dir, "..", "backend", "data"))
    os.makedirs(backend_data_dir, exist_ok=True)
    filepath = os.path.join(backend_data_dir, "health_data.csv")

    # Clear file and write headers
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "spo2", "pulse"])

    while True:
        await asyncio.sleep(Write_Interval)
        if data_buffer:
            # Append mode so old data isn’t erased
            with open(filepath, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(data_buffer)
            print(f"CSV appended with {len(data_buffer)} rows.")
            data_buffer = []  # clear buffer for next interval



async def main():
    global DEVICE_ADDRESS, CHAR_UUID
    # global Write_Duration

    CHAR_UUID = await find_device()
    if CHAR_UUID == -1:
        print("Device not found.")
        return

    print(f"Using characteristic: {CHAR_UUID}")

    async with BleakClient(DEVICE_ADDRESS) as client:
        print("Connected. Subscribing to notifications...")
        await client.start_notify(CHAR_UUID, notification_handler)

        # Run CSV writer in parallel
        writer_task = asyncio.create_task(csv_writer())

        # Keep connection alive (adjust duration as needed)
        # await asyncio.sleep(Write_Duration)
        await asyncio.Event().wait()  # Run indefinitely

        await client.stop_notify(CHAR_UUID)
        writer_task.cancel()
        print("Stopped.")


asyncio.run(main())
