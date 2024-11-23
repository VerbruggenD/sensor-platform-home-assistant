import json

# Assuming you have Sensor classes imported
from sensorInterface import Sensor
from dht_sensor import DHT11Sensor
from switch import Switch
from bme680_sensor import Bme680Sensor

class Config:
    def __init__(self, macAddress):
        self.config_str = None
        self.sensors = []
        self.mqtt_client = None
        self.macAddress = macAddress
        self.config_received = False

    def handle_config(self, topic, payload):
        if self.macAddress not in payload:
            print("Received config for other device")
            return
        
        self.config_received = True
        self.parse_config(payload)

    def set_mqtt_client(self, client):
        self.mqtt_client = client
    
    def parse_config(self, json_str):
        """Parse JSON configuration and instantiate sensor objects."""
        # Load JSON data
        config_data = json.loads(json_str)
        
        # Process sensors
        self.sensors = []
        for sensor_data in config_data.get('sensors', []):
            sensor_type = sensor_data.get('type')
            name = sensor_data.get('name')
            room = sensor_data.get('room')
            pins = sensor_data.get('pins', {})
            
            if sensor_type == 'DHT11':
                # Handle DHT11 sensor
                self.sensors.append(DHT11Sensor(self.mqtt_client.client, name, room, pins, self.macAddress))
                print(f"Added DHT sensor {name} to list")
            elif sensor_type == 'BME680':
                # Handle BME280 sensor
                self.sensors.append(Bme680Sensor(self.mqtt_client.client, name, room, pins, self.macAddress))
                print(f"Added BME680 sensor {name} to list")
            # elif sensor_type == 'SPI_Sensor':
            #     # Handle SPI_Sensor
            #     self.sensors.append(SPISensor(name, room, pins, mac_address))
            else:
                print(f"Unknown sensor type: {sensor_type}")

        self.actuators = []
        for actuator_data in config_data.get('actuators', []):
            actuator_type = actuator_data.get('type')
            name = actuator_data.get('name')
            room = actuator_data.get('room')
            pins = actuator_data.get('pins', {})

            if actuator_type == 'switch':
                self.actuators.append(Switch(self.mqtt_client, name, room, pins, self.macAddress))
                print(f"Added relay {name} to list")
            
            else:
                print(f"Unknown actuator type: {actuator_type}")

    def read_sensors(self):
        """Iterate through all sensors and poll them if the interval has passed."""
        for sensor in self.sensors:
            sensor.poll_sensor()

# # Example usage
# config_json = '''
# {
#     "sensors": [
#         {
#             "type": "DHT11",
#             "name": "Living Room DHT11",
#             "interface": "IO",
#             "pins": {
#                 "data": 21
#             },
#             "room": "Living Room"
#         },
#         {
#             "type": "DHT11",
#             "name": "Bedroom DHT11",
#             "interface": "IO",
#             "pins": {
#                 "data": 12
#             },
#             "room": "Bedroom"
#         },
#         {
#             "type": "BME280",
#             "name": "Office BME280",
#             "interface": "I2C",
#             "pins": {
#                 "sda": 21,
#                 "scl": 22
#             },
#             "i2c_address": "0x76",
#             "room": "Office"
#         },
#         {
#             "type": "SPI_Sensor",
#             "name": "Garage SPI Sensor",
#             "interface": "SPI",
#             "pins": {
#                 "miso": 19,
#                 "mosi": 23,
#                 "sclk": 18,
#                 "cs": 5
#             },
#             "spi_bus": 1,
#             "room": "Garage"
#         }
#     ]
# }
# '''

# config = Config("12-34-56-78-90-12")
# config.parse_config(config_json)

# # Print out the parsed sensors and MQTT configuration
# for sensor in config.sensors:
#     print(f"Sensor Name: {sensor.name}, Type: {sensor.type}, Room: {sensor.room}")
