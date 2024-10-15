# from dht_sensor import DHT11Sensor
import wifi
import mqtt
import _thread  # Using _thread for threading in MicroPython
import time

from config import Config

# Constants
TIMEOUT = 30  # Time to wait for a response before retrying (in seconds)

# Global variable for tracking requests
request_pending = False

def request_config(client, mac_address):
    global request_pending
    try:
        print(f"Requesting config for {mac_address}")
        client.client.publish("general/config_request", mac_address)
        request_pending = True
        return time.time()
    except Exception as e:
        print(f"Error: Failed to publish config request - {e}")
        return None

# Main function
def main():

    # 1 connect to wifi
    wifi.connect_wifi()

    macAddress = wifi.get_mac_address()

    print(f"mac address is {macAddress}")

    client = mqtt.MQTTHandler(macAddress)

    if not client:
        print("Failed connecting to mqtt broker...")
        return
    
    global config
    config = Config(macAddress)

    client.set_config_handler(config)

    config.set_mqtt_client(client.client)

    # Subscribe to the config response topic
    client.subscribe("general/config_response")
    client.subscribe(f"heartbeat/{macAddress}")

    # Retry mechanism
    last_request_time = request_config(client, macAddress)  # Send initial request
    config_received = False

    if not last_request_time:
        last_request_time = 0

    while not config_received:
        # Check for incoming messages (non-blocking)
        client.check_messages()
        
        # Check if config has been received
        if config.config_received:  # Assuming `config_received` is set in the config handler
            config_received = True
            break

        # Timeout and retry logic
        current_time = time.time()
        if current_time - last_request_time > TIMEOUT:
            print("Timeout reached, re-sending config request...")
            last_request_time = request_config(client, macAddress)
            if not last_request_time:
                last_request_time = 0

        time.sleep(0.1)  # Small delay to avoid busy looping

    print("Config received, proceeding with the rest of the program...")

    # Main loop: keep checking for incoming messages
    try:
        print("Starting loop")
        while True:
            client.check_messages()  # Continually check for messages
            config.read_sensors()
            time.sleep(0.5)
    
    except OSError as e:
        print(f"OSError occurred: {e}. Reconnecting...")
        client.connect()  # Reconnect on error

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        client.client.disconnect()

if __name__ == "__main__":
    main()