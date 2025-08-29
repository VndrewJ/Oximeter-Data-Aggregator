import socket, pickle

HEADERSIZE = 10

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((socket.gethostname(), 1243))

full_msg = b""
new_msg = True

while True:
    msg = client.recv(16)
    if not msg:
        print("Connection closed by server")
        break

    if new_msg:
        header = msg[:HEADERSIZE]
        msglen = int(header.decode().strip())
        new_msg = False
        print(f"Expecting message of length {msglen}")

    full_msg += msg

    if len(full_msg) - HEADERSIZE == msglen:
        data = pickle.loads(full_msg[HEADERSIZE:])
        print("Received data_buffer:", data)  # e.g. [ts, hr, spo2]

        # reset for next message
        new_msg = True
        full_msg = b""
client.close()