import asyncio
from bleak import BleakClient
import matplotlib.pyplot as plt
import numpy as np
import csv

DEVICE_ADDRESS = "6C:79:B8:D5:1D:30"
CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

# Buffers
segment_buffer = []

waveform_data_1 = []
waveform_data_2 = []

spo2_data = []
hr_data = []

timestamps_1 = []
timestamps_2 = []

sample_index_1 = 0
sample_index_2 = 0

def notification_handler(sender, data):
    global segment_buffer, sample_index_1, sample_index_2

    packet = list(data)
    if not packet:
        return

    # Detect start of a new frame
    if packet[0] == 170:
        segment_buffer = [packet]
    elif segment_buffer:
        segment_buffer.append(packet)

    # Wait for 4 segments
    if len(segment_buffer) == 4:
        # Flatten full frame
        full_frame = [byte for segment in segment_buffer for byte in segment]
        segment_buffer.clear()

        # Sanity check
        if len(full_frame) < 38:
            return

        # Extract waveform (bytes 5–34 = 30 values)
        waveform_1 = full_frame[5:35]
        waveform_data_1.extend(waveform_1)

        waveform_2 = full_frame[38:65]
        waveform_data_2.extend(waveform_2)

        # Time index for waveform
        timestamps_1.extend(range(sample_index_1, sample_index_1 + len(waveform_1)))

        timestamps_2.extend(range(sample_index_2, sample_index_2 + len(waveform_2)))

        sample_index_1 += len(waveform_1)  
        sample_index_2 += len(waveform_2)


        # Extract SpO₂ and HR
        spo2 = full_frame[36]
        hr = full_frame[37]

        if 0 < spo2 < 127 and 0 < hr < 255:
            spo2_data.append(spo2)
            hr_data.append(hr)
        else:
            spo2_data.append(None)
            hr_data.append(None)

async def main():
    async with BleakClient(DEVICE_ADDRESS) as client:
        print("Connected. Collecting data for 30 seconds...")
        await client.start_notify(CHAR_UUID, notification_handler)
        await asyncio.sleep(30)
        await client.stop_notify(CHAR_UUID)
        print("Data collection complete.")

        # Plot waveform
        plt.figure(figsize=(10, 4))
        plt.plot(timestamps_1, waveform_data_1, label="PPG Waveform")
        plt.title("PPG Waveform")
        plt.xlabel("Sample Index")
        plt.ylabel("Amplitude")
        plt.grid(True)
        plt.legend()

        # Plot waveform
        plt.figure(figsize=(10, 4))
        plt.plot(timestamps_2, waveform_data_2, label="Other Waveform")
        plt.title("Other Waveform")
        plt.xlabel("Sample Index")
        plt.ylabel("Amplitude")
        plt.grid(True)
        plt.legend()

        # Plot SpO₂ and HR
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

        # Save data to CSV
        print("Saving to 'pulse_oximeter_data.csv'...")
        with open("pulse_oximeter_data.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Sample Index", "PPO Waveform", "Other Waveform", "SpO2", "Heart Rate"])
            for i in range(len(waveform_data_1)):
                spo2_idx = i // 60  # one SpO2 value per 60 waveform samples
                spo2 = spo2_data[spo2_idx] if spo2_idx < len(spo2_data) else ""
                hr = hr_data[spo2_idx] if spo2_idx < len(hr_data) else ""
                writer.writerow([timestamps_1[i], waveform_data_1[i], waveform_data_2[i], spo2, hr])
        print("CSV saved.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted by user.")
