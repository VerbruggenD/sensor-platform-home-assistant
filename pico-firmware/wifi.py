import network
import time
import ubinascii
import os
import credentials

# Wi-Fi credentials
wifi_ssid = credentials.wifi_ssid
wifi_password = credentials.wifi_password

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)
    
    while not wlan.isconnected():
        print('Connecting to WiFi...')
        time.sleep(1)
    
    print('Connected to WiFi:', wlan.ifconfig())

def get_mac_address():
    wlan = network.WLAN(network.STA_IF)
    mac_address = ubinascii.hexlify(wlan.config('mac'), ':').decode()
    mac_address = mac_address.replace(":", "-")
    return mac_address

def check_connected():
    wlan = network.WLAN(network.STA_IF)
    return wlan.isconnected()

def reconnect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)

def disconnect():
    wlan = network.WLAN(network.STA_IF)
    wlan.disconnect()
    wlan.active(False)