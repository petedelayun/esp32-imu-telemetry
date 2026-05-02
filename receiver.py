import socket
import csv
from datetime import datetime
from config import PORT

LOG_FILE = "telemetry.csv"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))

print("Listening for telemetry...")

with open(LOG_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "ticks_ms", "ax", "ay", "az", "gx", "gy", "gz"])

    while True:
        data, addr = sock.recvfrom(1024)
        row = data.decode().strip().split(",")
        wall_time = datetime.now().isoformat()
        writer.writerow([wall_time] + row)
        f.flush()
        print(f"[{wall_time}] ax={row[1]} ay={row[2]} az={row[3]}")