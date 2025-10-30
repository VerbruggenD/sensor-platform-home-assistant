import network
import time
import ubinascii
import os
import credentials

# Wi-Fi credentials
wifi_ssid = credentials.wifi_ssid
wifi_password = credentials.wifi_password

def connect_wifi():
    """
    Connect to the Wi-Fi network using the provided SSID and password.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)
    
    while not wlan.isconnected():
        print('Connecting to WiFi...')
        time.sleep(1)
    
    print('Connected to WiFi:', wlan.ifconfig())

def get_mac_address():
    """
    Retrieve the MAC address of the Wi-Fi interface and format it.

    Returns:
        str: The formatted MAC address (e.g., "AA-BB-CC-DD-EE-FF").
    """
    wlan = network.WLAN(network.STA_IF)
    mac_address = ubinascii.hexlify(wlan.config('mac'), ':').decode()
    mac_address = mac_address.replace(":", "-")
    return mac_address

def check_connected():
    """
    Check if the device is connected to the Wi-Fi network.

    Returns:
        bool: True if connected, False otherwise.
    """
    wlan = network.WLAN(network.STA_IF)
    return wlan.isconnected()

def reconnect():
    """
    Reconnect to the Wi-Fi network.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)

def disconnect():
    """
    Disconnect from the Wi-Fi network.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.disconnect()
    wlan.active(False)