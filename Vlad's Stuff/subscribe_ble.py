from bleak import BleakClient
import asyncio

DEVICE_ADDRESS = "6C:79:B8:D5:1D:30"
CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

# Global variables to accumulate values
spo2_sum = 0
hr_sum = 0
count = 0

def notification_handler(sender, data):
    global spo2_sum, hr_sum, count

    print(f"{list(data)}")
    # print(f"Hex: {data.hex()}")

    # if len(data) >= 3:

    #     # for d in data:
    #     #     print(f"-> count: {count} ->byte: {d} -> hex: {d:02x}")
    #     #     count += 1
        
    #     if count == 1 and data[16] != 127 and data[17] != 255 and data[16] != 0 and data[16] != 0:
    #         spo2_sum = data[16]
    #         hr_sum = data[17]
    #         print(f"spO2: {spo2_sum}, HR: {hr_sum}")
        
    #     if data[0] == 170:
    #         count += 1
    #     else:
    #         count = 0

    # else:
    #     print("Data length too short for SpO2 and HR decoding.")

async def main():
    async with BleakClient(DEVICE_ADDRESS) as client:
        print("Connected. Subscribing to notifications...")
        await client.start_notify(CHAR_UUID, notification_handler)
        await asyncio.sleep(10)  # Listen for 30 seconds
        await client.stop_notify(CHAR_UUID)
        print("Stopped.")

asyncio.run(main())
