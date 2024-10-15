import json
import os
import paho.mqtt.client as mqtt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

broker_address = os.getenv('MQTT_BROKER_HOST')  # Replace with your broker address
broker_port = os.getenv('MQTT_BROKER_PORT')
username = os.getenv('MQTT_USERNAME')
password = os.getenv('MQTT_PASSWORD')

sensor_configs = {}

def on_connect(client, userdata, flags, reason_code):
    logging.info(f"Connected with result code {reason_code}")
    client.subscribe("general/config_request")

def on_message(client, userdata, message):
    payload = message.payload.decode()
    try:
        mac_address = payload
        logging.info(f"Payload MAC address is {mac_address}")
        
        sensor_config = sensor_configs.get(mac_address)
        
        if sensor_config:
            response_message = json.dumps(sensor_config)
            client.publish("general/config_response", response_message)
            logging.info(f"Published config for MAC address {mac_address}: {response_message}")
        else:
            logging.warning(f"No configuration found for MAC address {mac_address}")
    
    except json.JSONDecodeError:
        logging.error("Received invalid JSON data")

def load_sensor_configs(config_folder):
    global sensor_configs
    
    for filename in os.listdir(config_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(config_folder, filename)
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                mac_address = json_data.get('mac-address')
                sensors = json_data.get('sensors', [])
                
                if mac_address and sensors:
                    mac_address_normalized = mac_address.replace(":", "-")
                    json_data['mac-address'] = mac_address_normalized
                    sensor_configs[mac_address_normalized] = json_data
    logging.info(f"All {len(sensor_configs)} sensors loaded")
    
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
