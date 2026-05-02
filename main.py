import network
import socket
import time
import struct
from machine import I2C, Pin
from config import WIFI_SSID, WIFI_PASSWORD, COMPUTER_IP, PORT

MPU_ADDR = 0x68
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
i2c.writeto_mem(MPU_ADDR, 0x6B, b'\x00')

def read_raw(reg):
    data = i2c.readfrom_mem(MPU_ADDR, reg, 2)
    return struct.unpack('>h', data)[0]

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)

print("Connecting to WiFi...")
while not wlan.isconnected():
    time.sleep(0.1)
print("Connected:", wlan.ifconfig()[0])

# UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Broadcasting telemetry...")
while True:
    ax = read_raw(0x3B) / 16384.0
    ay = read_raw(0x3D) / 16384.0
    az = read_raw(0x3F) / 16384.0
    gx = read_raw(0x43) / 131.0
    gy = read_raw(0x45) / 131.0
    gz = read_raw(0x47) / 131.0

    msg = f"{time.ticks_ms()},{ax:.3f},{ay:.3f},{az:.3f},{gx:.3f},{gy:.3f},{gz:.3f}"
    sock.sendto(msg.encode(), (COMPUTER_IP, PORT))
    time.sleep(0.05)
