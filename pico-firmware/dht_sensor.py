from sensorInterface import Sensor, Measurement
import machine
import dht
import time

# Specific Sensor Implementation for DHT11
class DHT11Sensor(Sensor):
    def __init__(self, mqtt_client, name, room, pins, mac_address):
        super().__init__(name, room, "DHT11", "digital-IO", pins, mac_address, 10)
        
        # Initialize the sensor on the specified pin
        self.dht_pin = machine.Pin(pins['data'])  # Access the pin using key 'data'
        self.dht_sensor = dht.DHT11(self.dht_pin)  # Instantiate the DHT11 sensor
        
        # Create a dictionary for measurements instead of a list
        self.measurements = {
            "temperature": Measurement(self, "temperature", "C"),
            "humidity": Measurement(self, "humidity", "%")
        }

        self.set_mqtt_client(mqtt_client)
        self.discover()
    
    def read_measurement(self):
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
