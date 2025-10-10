############################################
##### SENSOR PLATFORM - HOME ASSISTANT #####
############################################
# Developer: Dieter Verbruggen
# File: pico-firmware/install/install.py

## IMPORTS ##
import mip

import network
import time

from credentials import wifi_ssid, wifi_password

## WIFI CONNECTION ##
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)

while not wlan.isconnected():
    print("Connecting...")
    time.sleep(1)

print("Connected:", wlan.ifconfig())

### INSTALLATION OF REQUIRED LIBRARIES ##
mip.install('umqtt.simple')
mip.install('dht')