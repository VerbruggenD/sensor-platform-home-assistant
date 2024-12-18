import json
import os
import time
import paho.mqtt.client as mqtt
from enum import Enum
from datetime import datetime
import threading
import logging

from logging.handlers import TimedRotatingFileHandler

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

def on_heartbeat_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Heartbeat thread connected successfully")
    else:
        logger.error(f"Heartbeat thread connection failed with result code {rc}")
    client.subscribe("heartbeat/response")

def on_heartbeat_message(client, userdata, msg):
    mac_address = msg.payload.decode("utf-8")
    logger.info(f"Received response {mac_address}")
    if mac_address in devices:
        devices[mac_address].newPing(True)  # Device responded, mark it as online
        if mac_address in device_events:
            device_events[mac_address].set()
            del device_events[mac_address]

def send_heartbeat(mac_address):
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
    devices[mac_address].newPing(False)
    logger.warning(f"No response from {mac_address}, current state: {devices[mac_address].state}")

class State(Enum):
    ONLINE = 1
    DISRUPTED = 2
    OFFLINE = 3
    DISABLED = 4

class DeviceHeartbeat:
    def __init__(self, macAddress, sensors, actuators, state):
        self.macAddress = macAddress
        self.state = state
        self.sensors = sensors
        self.actuators = actuators

    def publish_availability(self, availability):
        try:
            for sensor in self.sensors:
                topic = f"{sensor['room']}/{self.macAddress}-{sensor['name']}/availability"
                mqttc_heartbeat.publish(topic, payload=availability, qos=0)
                logger.info(f"Published '{availability}' to {topic}")
            for actuator in self.actuators:
                topic = f"{actuator['room']}/{self.macAddress}-{actuator['name']}/availability"
                mqttc_heartbeat.publish(topic, payload=availability, qos=0)
                logger.info(f"Published '{availability}' to {topic}")
        except Exception as e:
            logger.error(f"Failed to publish availability for {self.macAddress}: {e}")

    def badPing(self):
        if self.state == State.DISRUPTED:
            self.state = State.OFFLINE
            self.publish_availability("offline")
        elif self.state == State.ONLINE:
            self.state = State.DISRUPTED

    def goodPing(self):
        if self.state == State.DISABLED:
            return
        if self.state != State.ONLINE:
            self.state = State.ONLINE
            self.publish_availability("online")

    def newPing(self, result):
        if self.state == State.DISABLED:
            return
        if not result:
            self.badPing()
        else:
            self.goodPing()

def load_sensor_configs(config_folder):
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
                            devices[mac_address_normalized] = DeviceHeartbeat(mac_address_normalized, sensors, actuators, State.OFFLINE)
        logger.info(f"Loaded sensor configurations for {len(devices)} devices")
    except Exception as e:
        logger.error(f"Failed to load sensor configurations: {e}")

    return sensor_configs

def main():
    global mqttc_heartbeat

    config_folder = 'config'
    global sensor_configs
    sensor_configs = load_sensor_configs(config_folder)
    
    try:
        mqttc_heartbeat = mqtt.Client()
        mqttc_heartbeat.username_pw_set(username, password)
        mqttc_heartbeat.on_connect = on_heartbeat_connect
        mqttc_heartbeat.on_message = on_heartbeat_message
        mqttc_heartbeat.connect(broker_address, broker_port, 60)

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
