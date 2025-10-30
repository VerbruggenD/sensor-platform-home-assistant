import json

# Assuming you have Sensor classes imported
from sensorInterface import Sensor
from dht_sensor import DHT11Sensor
from switch import Switch
from bme680_sensor import Bme680Sensor

class Config:
    """
    Holds everything to do with the configuration of the node.
    """
    def __init__(self, mac_address):
        """
        Init of the config class. Everything initialized empty/None except mac address.

        Parameters:
            mac_address (string): the mac address of the wifi interface
        """
        self.config_str = None
        self.sensors = []
        self.actuators = []
        self.mqtt_client = None
        self.mac_address = mac_address
        self.config_received = False

    def handle_config(self, payload):
        """
        Handle new incoming config.

        Parameters:
            payload (string): json as a string containing the actual config object to parse and create the instances.
        """
        if self.mac_address not in payload:
            print("Received config for other device")
            return
        
        self.config_received = True
        self.parse_config(payload)

    def set_mqtt_client(self, client):
        """
        Set the mqtt client for passing to the instances.

        Parameters:
            client (umqtt.Client): the client passed to the instances.
        """
        self.mqtt_client = client

    def set_default_state(self, publish=True):
        """
        Activate the default state of the actuator.

        Parameters:
            publish (boolean): select if the state change needs to be published.
        """
        for actuator in self.actuators:
            actuator.set_default_state(publish)

    def resubscribe(self):
        """
        Resubscribe to the command topics for every actuator registered in the list.
        """
        for actuator in self.actuators:
            actuator.subscribe_set()

    def send_state(self):
        """
        Send the current state of every actuator in the list.
        """
        for actuator in self.actuators:
            actuator.publish_state()
    
    def parse_config(self, json_str):
        """
        Parse JSON configuration and instantiate sensor objects.
        
        Parameters:
            json_str (string): json string containing the config for the sensor/actuator instance.
        """
        # Load JSON data
        config_data = json.loads(json_str)
        
        # Process sensors
        self.sensors = []
        for sensor_data in config_data.get('sensors', []):
            sensor_type = sensor_data.get('type')
            
            if sensor_type == 'DHT11':
                # Handle DHT11 sensor
                self.sensors.append(DHT11Sensor(self.mqtt_client.client, self.mac_address, sensor_data))
                print(f"Added DHT sensor to list")
            elif sensor_type == 'BME680':
                # Handle BME280 sensor
                self.sensors.append(Bme680Sensor(self.mqtt_client.client, self.mac_address, sensor_data))
                print(f"Added BME680 sensor to list")
            else:
                print(f"Unknown sensor type: {sensor_type}")

        self.actuators = []
        for actuator_data in config_data.get('actuators', []):
            actuator_type = actuator_data.get('type')

            if actuator_type == 'switch':
                self.actuators.append(Switch(self.mqtt_client, self.mac_address, actuator_data))
                print(f"Added relay {name} to list")
            
            else:
                print(f"Unknown actuator type: {actuator_type}")

    def read_sensors(self):
        """
        Iterate through all sensors and poll them if the interval has passed.
        """
        for sensor in self.sensors:
            sensor.poll_sensor()
