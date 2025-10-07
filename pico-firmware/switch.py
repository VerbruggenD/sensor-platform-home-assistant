from actuatorinterface import Actuator, State
from machine import Pin
import time
import json

class Switch(Actuator):
    def __init__(self, mqtt_client, name, room, pins, mac_address, defaultState):
        super().__init__(name, room, "Switch", "digital-IO", pins, mac_address, defaultState)

        # self.relay_pin = machine.Pin(pins['data'])
        self.relay_pin = Pin(pins['data'], Pin.OUT)
        
        self.set_mqtt_client(mqtt_client)

        self.interval = 600
        self.last_update = 0

        # Define and add ON and OFF states
        self.add_state(State("ON"))
        self.add_state(State("OFF"))

        self.subscribe_set()
        self.discover()
        self.set_default_state()

    def update_actuator(self):
        """Update the relay pin state based on the current state."""
        if self.state.name == "ON":
            self.relay_pin.value(1)
            print("Updated switch to ON")
        elif self.state.name == "OFF":
            self.relay_pin.value(0)
            print("Updated switch to OFF")
        else:
            print(f"Unknown state: {self.state}")

    def on_message(self, topic, payload):
        try:
            if topic == self.command_topic:
                
                # Call the set_state function
                self.set_state(payload)
        except Exception as e:
            print(f"Error processing message: {e}")

    def set_default_state(self, publish=True):
        self.set_state(self.defaultState, publish)

    