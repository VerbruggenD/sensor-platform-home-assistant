import json
import os
import time
import paho.mqtt.client as mqtt
from datetime import datetime
import threading
import logging

from logging.handlers import TimedRotatingFileHandler

from heartbeat import DeviceHeartbeat, State

# Create a logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)  # Set the log level (DEBUG, INFO, WARNING, etc.)

# Create a TimedRotatingFileHandler
log_file = 'log/heartbeat.log'
file_handler = TimedRotatingFileHandler(
    log_file, 
    when='midnight',  # Rotate logs at midnight
    interval=1,       # Rotate every 1 day
    backupCount=7     # Keep logs for 7 days (1 week)
)

# Create a StreamHandler for terminal logging
console_handler = logging.StreamHandler()

# Create a formatter and add it to both handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Access environment variables
broker_address = os.environ.get('BROKER_ADDRESS')
broker_port = int(os.environ.get('BROKER_PORT', 1883))
username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')

logger.info(f"Broker Address: {broker_address}")
logger.info(f"Broker Port: {broker_port}")
logger.info(f"Username: {username}")
logger.info(f"Password: {password}")

logger.info(f"Broker Address: {broker_address} (type: {type(broker_address)})")
logger.info(f"Broker Port: {broker_port} (type: {type(broker_port)})")
logger.info(f"Username: {username} (type: {type(username)})")
logger.info(f"Password: {password} (type: {type(password)})")

sensor_configs = {}
devices = {}
device_events = {}

def on_heartbeat_connect(client, rc):
    """
    Callback when the heartbeat client connects to the MQTT broker.

    Parameters:
        client: The MQTT client instance.
        rc: The connection result code.
    """
    if rc == 0:
        logger.info("Heartbeat thread connected successfully")
    else:
        logger.error(f"Heartbeat thread connection failed with result code {rc}")
    client.subscribe("heartbeat/response")

def on_heartbeat_message(msg):
    """
    Callback when a heartbeat response message is received.

    Parameters:
        msg: The received MQTT message.
    """
    mac_address = msg.payload.decode("utf-8")
    logger.info(f"Received response {mac_address}")
    if mac_address in devices:
        devices[mac_address].handleNewPing(True)  # Device responded, mark it as online
        if mac_address in device_events:
            device_events[mac_address].set()
            del device_events[mac_address]

def send_heartbeat(mac_address):
    """
    Send a heartbeat ping to the specified MAC address.

    Parameters:
        mac_address (str): The MAC address of the device.
    """
    topic = f"heartbeat/{mac_address}"
    try:
        mqttc_heartbeat.publish(topic, payload="ping", qos=0)
        # logger.info(f"Sent heartbeat to {topic}")

        event = threading.Event()
        device_events[mac_address] = event

        if not event.wait(timeout=5.0):
            handle_timeout(mac_address)
        # else:
        #     logger.info(f"Heartbeat response received in time for {mac_address}. Current state: {devices[mac_address].state}")

    except Exception as e:
        logger.error(f"Failed to send heartbeat to {mac_address}: {e}")

def handle_timeout(mac_address):
    """
    Handle a timeout for the specified MAC address.

    Parameters:
        mac_address (str): The MAC address of the device.
    """
    devices[mac_address].handleNewPing(False)
    logger.warning(f"No response from {mac_address}, current state: {devices[mac_address].state}")

def load_sensor_configs(config_folder):
    """
    Load sensor configurations from JSON files in the specified folder.

    Parameters:
        config_folder (str): The folder containing JSON configuration files.
    """
    global devices
    sensor_configs = {}
    
    try:
        for filename in os.listdir(config_folder):
            if filename.endswith('.json'):
                file_path = os.path.join(config_folder, filename)
                with open(file_path, 'r') as file:
                    json_data = json.load(file)
                    mac_address = json_data.get('mac-address')
                    sensors = json_data.get('sensors', [])
                    actuators = json_data.get('actuators', [])
                    
                    if mac_address and (sensors or actuators):
                        mac_address_normalized = mac_address.replace(":", "-")
                        json_data['mac-address'] = mac_address_normalized
                        sensor_configs[mac_address_normalized] = json_data
                        
                        if mac_address_normalized not in devices:
                            devices[mac_address_normalized] = DeviceHeartbeat(mac_address_normalized, sensors, actuators, State.OFFLINE, mqttc_heartbeat)
        logger.info(f"Loaded sensor configurations for {len(devices)} devices")
    except Exception as e:
        logger.error(f"Failed to load sensor configurations: {e}")

    return sensor_configs

def main():
    global mqttc_heartbeat

    config_folder = 'config'
    global sensor_configs
    
    try:
        mqttc_heartbeat = mqtt.Client()
        mqttc_heartbeat.username_pw_set(username, password)
        mqttc_heartbeat.on_connect = on_heartbeat_connect
        mqttc_heartbeat.on_message = on_heartbeat_message
        mqttc_heartbeat.connect(broker_address, broker_port, 60)

        sensor_configs = load_sensor_configs(config_folder)

        mqttc_heartbeat.loop_start()  # Start MQTT loop in background

        logger.info("Starting heartbeat logic thread")
        while True:
            cycle_start_time = time.time()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"Current time: {current_time}")

            for mac_address, device in devices.items():
                if device.state != State.DISABLED:
                    send_heartbeat(mac_address)
            
            cycle_duration = time.time() - cycle_start_time
            sleep_duration = max(0, 12 - cycle_duration)
            time.sleep(sleep_duration)
    
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}")

if __name__ == "__main__":
    main()
