import re
import pandas as pd

# Simulated raw string from your data file
raw_text = """
170 76 65 104 0 3 3 6 9 11 13 14 14 14 14 13 13 12 12 11 11 10 10 9 9 9 9 9 9 9 9 8 8 8 7 255 99 60 255 0
170 76 65 105 0 3 3 6 9 11 13 14 14 14 14 13 13 12 12 11 11 10 10 9 9 9 9 9 9 9 9 8 8 8 7 255 98 61 255 0
170 76 65 106 0 3 3 6 9 11 13 14 14 14 14 13 13 12 12 11 11 10 10 9 9 9 9 9 9 9 9 8 8 8 7 255 97 62 255 0
"""

# Parse the raw text into frames
def parse_frames(text):
    pattern = r"170\s(?:\d+\s+){37}\d+"
    matches = re.findall(pattern, text.strip())
    return [list(map(int, match.strip().split())) for match in matches]

# Decode each frame into useful data
def decode_frame(frame):
    if len(frame) < 40 or frame[0] != 170:
        return None
    return {
        "packet": frame[3],
        "spo2": frame[36],
        "pulse": frame[37],
        "waveform": frame[5:35],
    }

# Run decoding
frames = parse_frames(raw_text)
decoded = [decode_frame(f) for f in frames if decode_frame(f)]

# Flatten waveform for DataFrame
rows = []
for entry in decoded:
    for i, val in enumerate(entry["waveform"]):
        rows.append({
            "packet": entry["packet"],
            "spo2": entry["spo2"],
            "pulse": entry["pulse"],
            "waveform_sample_index": i,
            "waveform_value": val
        })

# Create a DataFrame
df = pd.DataFrame(rows)
print(df.head())

# Optional: Save to CSV
df.to_csv("pulse_oximeter_decoded.csv", index=False)
