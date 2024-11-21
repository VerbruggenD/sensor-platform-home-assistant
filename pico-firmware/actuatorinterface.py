import json

class Actuator:
    def __init__(self, name, room, actuator_type, interface, pins, mac_address, is_switch = True):
        self.name = name  # E.g., DHT11_1, needs to be unique
        self.room = room  # E.g., Living Room
        self.type = actuator_type  # E.g., DHT11
        self.interface = interface  # E.g., digital-IO / PWM / SPI / I2C
        self.pins = pins  # Dictionary of pins used
        self.mac_address = mac_address  # The MAC address passed from the main function
        self.mqtt_client = None
        self.state = None
        self.value = None
        self.is_switch = is_switch # switch by default, if false then light is used (can be dimmed)

        self.states = {}
        self.state_topic = f"{self.room}/{self.mac_address}-{self.name}/state" # topic to publish current state
        self.command_topic = f"{self.room}/{self.mac_address}-{self.name}/set" # Topic to set the value/state of the actuator

        # if it is a light
        self.brigtness_state_topic = f"{self.room}/{self.mac_address}-{self.name}/value/state"
        self.brigtness_command_topic = f"{self.room}/{self.mac_address}-{self.name}/value/set"

        self.discovery_topic = ""
        if self.is_switch:
            self.discovery_topic = f"homeassistant/switch/{self.mac_address}-{self.name}/config"
        else:
            self.discovery_topic = f"homeassistant/light/{self.mac_address}-{self.name}/config"

        self.discovery_topic = self.discovery_topic.replace(" ", "-")
        self.discovery_payload = {
            "name": f"{self.name}",
            "state_topic": self.state_topic,
            "command_topic": self.command_topic,
            "brightness_state_topic": self.brigtness_state_topic,
            "brightness_command_topic": self.brigtness_command_topic,
            "unique_id": f"{self.mac_address}-{self.name}",
            "availability_topic": f"{self.room}/{self.mac_address}-{self.name}/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
            "device": {
                "identifiers": [f"{self.mac_address}-{self.name}"],
                "name": self.name,
                "model": "MultiNode v1.1",
                "manufacturer": "Dieter Verbruggen"
            }
        }

    def update_actuator(self):
        """This method should be overridden by specific actuator implementation."""
        # should use state and value to update the actual hardware settings
        # binary, only on/off are used
        # PWM, value from 0 to 100 and on/off
        raise NotImplementedError("Subclasses should implement this method.")
    
    def set_state(self, state_name):
        """This method should be overridden by specific actuator implementations."""
        print(f"Setting state: {state_name}")
        if state_name in self.states:
            self.state = self.states[state_name]
            self.update_actuator()
            self.publish_state()

    def set_value(self, value):
        """This method updates the actuator value and triggers the update actuator."""
        if value is not None:
            self.value = value
            self.update_actuator()
            self.publish_brigtness()

    def publish_brigtness(self):
        """Publish the current value of the light dim level"""
        if self.mqtt_client is None:
            print("Mqtt client is not set")
            return
    
        self.mqtt_client.client.publish(self.brightness_state_topic, self.value)
    
    def set_mqtt_client(self, client):
        """Add a reference to the mqtt cleitn to send messages from here."""
        self.mqtt_client = client

    def add_state(self, state):
        """Add a new state to the actuator's states dictionary."""
        self.states[state.name] = state

    def discover(self):
        """Publish discovery message for the actuator."""
        if not self.mqtt_client.client:
            print("MQTT client is not set.")
            return
        
        self.mqtt_client.client.publish(self.discovery_topic, json.dumps(self.discovery_payload), qos=0)
        print(f"Published discovery to {self.discovery_topic}")

    def get_state(self):
        """Get the current actuator state."""
        return self.state
    
    def publish_state(self):
        """Publish the current state and value to the MQTT broker."""
    
        if not self.mqtt_client.client:
            print("MQTT client is not set.")
            return
        
        if self.state is None:
            print("No state to publish.")
            return
        
        print(f"Publishing state: {self.state_topic} {self.state.name}")
        self.mqtt_client.client.publish(self.state_topic, self.state.name)

    def subscribe_set(self):
        """Subscribe to the MQTT command topic."""
        if self.mqtt_client.client:
            self.mqtt_client.client.subscribe(self.command_topic)
            self.mqtt_client.add_handler(self)
            print(f"Subscribed to command topic {self.command_topic}")
        else:
            print("MQTT client not set. Cannot subscribe.")

class State:
    """Simple state class to hold state name and value."""
    def __init__(self, name, value=None):
        self.name = name
        self.value = value