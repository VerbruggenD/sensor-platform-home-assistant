from sensorInterface import Sensor, Measurement
from machine import I2C, Pin
import time
from bme680 import *

class Bme680Sensor(Sensor):
    def __init__(self, mqtt_client, name, room, pins, mac_address):
        super().__init__(name, room, "BME680", "I2C", pins, mac_address, 10)

        # Use integers for pins directly
        i2c = I2C(0, scl=Pin(17), sda=Pin(16))  # Replace with your SDA/SCL pins
        devices = i2c.scan()

        # if devices:
        #     print("I2C devices found:", [hex(device) for device in devices])
        # else:
        #     print("No I2C devices found.")
        #     return

        # self.bme = BME680_I2C(i2c)  # Pass the I2C object to the BME680 driver

        self.measurements = {
            "temperature": Measurement(self, "temperature", "C"),
            "humidity": Measurement(self, "humidity", "%"),
            "pressure": Measurement(self, "pressure", "hPa"),
            "gas": Measurement(self, "gas", "ohm")
        }

        self.set_mqtt_client(mqtt_client)
        self.discover()

    def read_measurement(self):
        if len(self.measurements) == 0:
            return
        try:
            temperature = self.bme.temperature
            humidity = self.bme.humidity
            pressure = self.bme.pressure
            gas = self.bme.gas

            self.measurements["temperature"].publish_value(self.mqtt_client, temperature)
            self.measurements["humidity"].publish_value(self.mqtt_client, humidity)
            self.measurements["pressure"].publish_value(self.mqtt_client, pressure)
            self.measurements["gas"].publish_value(self.mqtt_client, gas)

            print(f"Current temp {temperature} humidity {humidity} pressure {pressure} gas {gas}")

        except OSError as e:
            print(f"Failed to read BME680 sensor: {e}")
            return {"temperature": None, "humidity": None, "pressure": None, "gas": None}