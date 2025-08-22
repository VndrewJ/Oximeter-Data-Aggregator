import asyncio
from bleak import BleakClient
import matplotlib.pyplot as plt

DEVICE_ADDRESS = "6C:79:B8:D5:1D:30"
CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

# Buffers
segment_buffer = []
waveform_data = []
spo2_data = []
hr_data = []
timestamps = []

# Track sample time
sample_index = 0

def notification_handler(sender, data):
    global segment_buffer, sample_index

    packet = list(data)

    if not packet:
        return

    # Segment 1 starts a new frame
    if packet[0] == 170:
        segment_buffer = [packet]
    elif segment_buffer:
        segment_buffer.append(packet)

    # If we have 4 segments, process the full frame
    if len(segment_buffer) == 4:
        full_frame = segment_buffer
        segment_buffer = []  # reset for next frame

        # Extract waveform data from all 4 segments (bytes 5–14 in each = 10 bytes × 4 = 40)
        full_waveform = []
        for segment in full_frame:
            if len(segment) >= 15:
                full_waveform.extend(segment[5:15])
        waveform_data.extend(full_waveform)
        timestamps.extend(range(sample_index, sample_index + len(full_waveform)))
        sample_index += len(full_waveform)

        # Extract SpO2 and HR from segment 2 (must exist and have enough length)
        if len(full_frame) >= 2 and len(full_frame[1]) >= 18:
            spo2 = full_frame[1][16]
            hr = full_frame[1][17]

            # Validate
            if 0 < spo2 < 127 and 0 < hr < 255:
                spo2_data.append(spo2)
                hr_data.append(hr)
            else:
                spo2_data.append(None)
                hr_data.append(None)


async def main():
    async with BleakClient(DEVICE_ADDRESS) as client:
        print("Connected. Collecting data for 10 seconds...")
        await client.start_notify(CHAR_UUID, notification_handler)
        await asyncio.sleep(10)
        await client.stop_notify(CHAR_UUID)
        print("Data collection complete.")

        # Plot waveform
        plt.figure(figsize=(10, 4))
        plt.plot(timestamps, waveform_data, label="Waveform")
        plt.title("PPG Waveform")
        plt.xlabel("Sample Index")
        plt.ylabel("Amplitude")
        plt.grid(True)
        plt.legend()

        # Plot SpO2 and HR
        plt.figure(figsize=(10, 4))
        plt.plot(spo2_data, label="SpO₂ (%)", marker='o')
        plt.plot(hr_data, label="Heart Rate (bpm)", marker='x')
        plt.title("SpO₂ and Heart Rate Over Time")
        plt.xlabel("Frame Index")
        plt.ylabel("Value")
        plt.grid(True)
        plt.legend()

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    asyncio.run(main())
