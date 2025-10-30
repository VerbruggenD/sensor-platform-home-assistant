from sensorInterface import Sensor, Measurement
import machine
import dht
import time

# Specific Sensor Implementation for DHT11
class DHT11Sensor(Sensor):
    def __init__(self, mqtt_client, name, room, pins, mac_address):
        """
        Initialize the DHT11 sensor.

        Parameters:
            mqtt_client: The MQTT client for publishing data.
            name (str): The name of the sensor.
            room (str): The room where the sensor is located.
            pins (dict): The pin configuration for the sensor.
            mac_address (str): The MAC address of the device.
        """
        super().__init__(name, room, "DHT11", "digital-IO", pins, mac_address, 10)
        
        # Initialize the sensor on the specified pin
        self.dht_pin = machine.Pin(pins['data'])  # Access the pin using key 'data'
        self.dht_sensor = dht.DHT11(self.dht_pin)  # Instantiate the DHT11 sensor
        
        # Create a dictionary for measurements instead of a list
        self.measurements = {
            "temperature": Measurement(self, "temperature", "\u00B0C"),  # Degree Celsius symbol
            "humidity": Measurement(self, "humidity", "%")
        }

        self.set_mqtt_client(mqtt_client)
        self.discover()
    
    def read_measurement(self):
        """
        Read measurements from the DHT11 sensor and publish them via MQTT.

        Returns:
            dict: A dictionary containing temperature and humidity readings.
        """
        try:
            self.dht_sensor.measure()  # Trigger measurement
            
            # Read temperature and humidity
            temperature = self.dht_sensor.temperature()  # Temperature in Celsius
            humidity = self.dht_sensor.humidity()  # Humidity percentage
            
            # Publish values via MQTT
            self.measurements["temperature"].publish_value(self.mqtt_client, temperature)
            self.measurements["humidity"].publish_value(self.mqtt_client, humidity)

            print(f"current temp {temperature} humidity {humidity}")
        
        except OSError as e:
            print(f"Failed to read DHT11 sensor: {e} on pin {self.dht_pin}")
            return {"temperature": None, "humidity": None}
