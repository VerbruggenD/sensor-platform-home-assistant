import json

class Sensor:
    def __init__(self, name, room, sensor_type, interface, pins, mac_address):
        self.name = name  # E.g., DHT11_1, needs to be unique
        self.room = room  # E.g., Living Room
        self.type = sensor_type  # E.g., DHT11
        self.interface = interface  # E.g., digital-IO / SPI / I2C
        self.pins = pins  # Dictionary of pins used
        self.mac_address = mac_address  # The MAC address passed from the main function
        self.mqtt_client = None
        
        # Using a dictionary for measurements instead of a list
        self.measurements = {}
    
    def read_measurement(self):
        """This method should be overridden by specific sensor implementations."""
        raise NotImplementedError("Subclasses should implement this method.")
    
    def set_mqtt_client(self, client):
        self.mqtt_client = client

    def add_measurement(self, measurement):
        """Add a new measurement to the sensor's measurements dictionary."""
        self.measurements[measurement.measurement_type] = measurement
    
    def discover(self):
        """Publish discovery messages for all measurements of the sensor."""
        if not self.mqtt_client:
            print("MQTT client is not set.")
            return
        
        print(f"Discovering {len(self.measurements)} measurements for sensor {self.name}")
        
        for measurement in self.measurements.values():
            measurement.discover(self.mqtt_client)
        
        print(f"Sent discovery topic for all measurements of sensor {self.name}")

    def poll_sensor(self):
        """Method to be overridden for polling logic."""
        pass

class Measurement:
    def __init__(self, sensor, measurement_type, unit):
        self.sensor = sensor  # Link to the sensor instance
        self.measurement_type = measurement_type  # E.g., "temperature" or "humidity"
        self.unit = unit  # E.g., "°C" or "%"
        self.state_topic = f"{sensor.room}/{sensor.mac_address}-{sensor.name}/{measurement_type}/state"
        
        # Automatically generate discovery topic and payload for Home Assistant, including MAC address
        self.discovery_topic = f"homeassistant/sensor/{sensor.mac_address}-{sensor.name}-{self.measurement_type}/config"
        self.discovery_topic = self.discovery_topic.replace(" ", "-")
        self.discovery_payload = {
            "name": f"{sensor.name} {measurement_type}",
            "state_topic": self.state_topic,
            "unit_of_measurement": self.unit.encode('utf-8').decode(),
            "device_class": measurement_type,
            "unique_id": f"{sensor.mac_address}-{sensor.name}-{measurement_type}",
            "availability_topic": f"{sensor.room}/{sensor.mac_address}-{sensor.name}/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
            "device": {
                "identifiers": [f"{sensor.mac_address}-{sensor.name}"],
                "name": sensor.name,
                "model": "MultiNode v1.0",
                "manufacturer": "Dieter Verbruggen"
            }
        }

    def publish_value(self, client, value):
        client.publish(self.state_topic, str(value), qos=0)
        print(f"published value to {self.state_topic}")
    
    def discover(self, client):
        client.publish(self.discovery_topic, json.dumps(self.discovery_payload), qos=0)
        print(f"Published discovery to {self.discovery_topic}")
