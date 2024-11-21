import network
import time

wifi_ssid = "telenet-E7B89D9"
wifi_password = "uMznf7kxuTch"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)

while not wlan.isconnected():
    print("Connecting...")
    time.sleep(1)

print("Connected:", wlan.ifconfig())
