from actuatorinterface import Actuator, State
from machine import Pin
import time
import json

class Switch(Actuator):
    def __init__(self, mqtt_client, name, room, pins, mac_address, defaultState):
        """
        Initialize the Switch actuator.

        Parameters:
            mqtt_client: The MQTT client for publishing data.
            name (str): The name of the switch.
            room (str): The room where the switch is located.
            pins (dict): The pin configuration for the switch.
            mac_address (str): The MAC address of the device.
            defaultState (str): The default state of the switch ("ON" or "OFF").
        """
        super().__init__(name, room, "Switch", "digital-IO", pins, mac_address, defaultState)

        # self.relay_pin = machine.Pin(pins['data'])
        self.relay_pin = Pin(pins['data'], Pin.OUT)
        
        self.set_mqtt_client(mqtt_client)

        self.interval = 600
        self.last_update = 0

        # Define and add ON and OFF states
        self.add_state(State("ON"))
        self.add_state(State("OFF"))

        self.subscribe_command_topic()
        self.publish_discovery()
        self.set_default_state()

    def update_actuator(self):
        """
        Update the relay pin state based on the current state.
        """
        if self.state.name == "ON":
            self.relay_pin.value(1)
            print("Updated switch to ON")
        elif self.state.name == "OFF":
            self.relay_pin.value(0)
            print("Updated switch to OFF")
        else:
            print(f"Unknown state: {self.state}")

    def on_message(self, topic, payload):
        """
        Handle incoming MQTT messages for the switch.

        Parameters:
            topic (str): The MQTT topic of the message.
            payload (str): The payload of the message.
        """
        try:
            if topic == self.command_topic:
                
                # Call the set_state function
                self.set_state(payload)
        except Exception as e:
            print(f"Error processing message: {e}")

    def set_default_state(self, publish=True):
        """
        Set the switch to its default state.

        Parameters:
            publish (bool): Whether to publish the state change to MQTT.
        """
        self.set_state(self.defaultState, publish)

    