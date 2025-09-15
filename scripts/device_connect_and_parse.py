from bleak import BleakScanner, BleakClient
import sqlite3
import asyncio
import time
import os
import uuid

DEVICE_ADDRESS = ""
CHAR_UUID = ""
Write_Interval = 5  # seconds

# Store the latest data
latest_data = {"hr": None, "spo2": None, "timestamp": None}
data_buffer = []
db_connection = None
current_session_id = None
session_key = None


async def create_session():
    """Create a new session with a unique key."""
    global current_session_id, session_key, db_connection

    session_key = str(uuid.uuid4())[:6].upper()
    cursor = db_connection.cursor()
    cursor.execute(
        "INSERT INTO session (session_key, start_time) VALUES (?, ?)",
        (session_key, int(time.time())),
    )
    db_connection.commit()
    current_session_id = cursor.lastrowid
    return session_key


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
    global latest_data, data_buffer, current_session_id
    raw = list(data)

    if len(raw) < 19:
        return

    try:
        if raw[18] == 255 and not (raw[15] == 255 and raw[16] == 127 and raw[17] == 255):
            spo2 = raw[16]
            hr = raw[17]
            ts = int(time.time())
            data_buffer.append((current_session_id, ts, spo2, hr))
            print(f"Session {session_key} -> HR={hr}, SpO₂={spo2}")
    except Exception as e:
        print("Parse error:", e)


async def db_writer():
    """Background task to write buffer to SQLite every interval."""
    global data_buffer, db_connection

    while True:
        await asyncio.sleep(Write_Interval)
        if data_buffer:
            try:
                cursor = db_connection.cursor()
                cursor.executemany(
                    "INSERT INTO health_data (session_id, timestamp, spo2, pulse) VALUES (?, ?, ?, ?)",
                    data_buffer,
                )
                db_connection.commit()
                print(f"DB appended with {len(data_buffer)} rows for session {session_key}")
                data_buffer = []  # clear buffer
            except Exception as e:
                print("DB write error:", e)


async def main():
    global DEVICE_ADDRESS, CHAR_UUID, db_connection, current_session_id

    # Get paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, ".."))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, "database.db")
    schema_path = os.path.join(base_dir, "schema.sql")

    # Initialize database
    db_connection = sqlite3.connect(db_path)
    with open(schema_path) as f:
        db_connection.executescript(f.read())

    # Create new session
    session_key = await create_session()
    print(f"Created new session: {session_key}")

    # Find device
    CHAR_UUID = await find_device()
    if CHAR_UUID == -1:
        print("Device not found.")
        return

    print(f"Using characteristic: {CHAR_UUID}")

    async with BleakClient(DEVICE_ADDRESS) as client:
        print(f"Connected. Starting session {session_key}")
        await client.start_notify(CHAR_UUID, notification_handler)

        # Run DB writer in parallel
        writer_task = asyncio.create_task(db_writer())

        try:
            # Run indefinitely until interrupted
            await asyncio.Event().wait()
        except (KeyboardInterrupt, asyncio.CancelledError):
            print(f"Stopping session {session_key}...")

        await client.stop_notify(CHAR_UUID)
        writer_task.cancel()
        print(f"Session {session_key} stopped.")


if __name__ == "__main__":
    asyncio.run(main())
