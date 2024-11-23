import json
import os
import paho.mqtt.client as mqtt
import logging

from logging.handlers import TimedRotatingFileHandler

# Create a logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)  # Set the log level (DEBUG, INFO, WARNING, etc.)

# Create a TimedRotatingFileHandler
log_file = 'config-server.log'
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

broker_address = os.getenv('MQTT_BROKER_HOST')  # Replace with your broker address
broker_port = os.getenv('MQTT_BROKER_PORT')
username = os.getenv('MQTT_USERNAME')
password = os.getenv('MQTT_PASSWORD')

sensor_configs = {}

def on_connect(client, userdata, flags, reason_code):
    logger.info(f"Connected with result code {reason_code}")
    client.subscribe("general/config_request")

def on_message(client, userdata, message):
    payload = message.payload.decode()
    try:
        mac_address = payload
        logger.info(f"Payload MAC address is {mac_address}")
        
        sensor_config = sensor_configs.get(mac_address)
        
        if sensor_config:
            response_message = json.dumps(sensor_config)
            client.publish("general/config_response", response_message)
            logger.info(f"Published config for MAC address {mac_address}: {response_message}")
        else:
            logger.warning(f"No configuration found for MAC address {mac_address}")
    
    except json.JSONDecodeError:
        logger.error("Received invalid JSON data")

def load_sensor_configs(config_folder):
    global sensor_configs
    
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
    logger.info(f"All {len(sensor_configs)} sensors or actuators loaded")
    
def main():
    config_folder = 'config'
    load_sensor_configs(config_folder)
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username, password)
    client.connect(broker_address, broker_port, 60)
    
    client.loop_forever()

if __name__ == "__main__":
    main()
