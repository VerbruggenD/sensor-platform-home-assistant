import json

class Actuator:
    def __init__(self, name, room, actuator_type, pins, mac_address, default_state, is_switch = True):
        """
        Initialize the actuator with its properties.

        Parameters:
            name (string): the name of the actuator.
            room (string): the room where the actuator is registered for, used in home assistant if it exists
            actuator_type (string): the type of the actuator of which an instance is created
            pins (dict): the pins registered for the instance for digital IO or data bus
            mac_address (string): mac address of the wifi of the rpi pico w
            default_state (State): the state to switch to on disconnect from broker/wifi
            is_switch (boolean): By default a switch, otherwise it's a light and this will publish brightness and can be dimmed
        """
        self.name = name  # E.g., DHT11_1, needs to be unique
        self.room = room  # E.g., Living Room
        self.type = actuator_type  # E.g., DHT11
        self.pins = pins  # Dictionary of pins used
        self.mac_address = mac_address  # The MAC address passed from the main function
        self.mqtt_client = None
        self.state = None
        self.value = None
        self.is_switch = is_switch # switch by default, if false then light is used (can be dimmed)
        self.defaultState = default_state

        self.states = {}
        self.state_topic = f"{self.room}/{self.mac_address}-{self.name}/state" # topic to publish current state
        self.command_topic = f"{self.room}/{self.mac_address}-{self.name}/set" # Topic to set the value/state of the actuator

        # if it is a light
        self.brigtness_state_topic = f"{self.room}/{self.mac_address}-{self.name}/value/state"
        self.brigtness_command_topic = f"{self.room}/{self.mac_address}-{self.name}/value/set"

        self.discovery_topic = f"homeassistant/{"switch" if self.is_switch else "light"}/{self.mac_address}-{self.name}/config"

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
        """
        This method should be overridden by specific actuator implementation.
        """
        # TODO: implement pwm with the use of brightness (lamp)
        raise NotImplementedError("Subclasses should implement this method.")
    
    def set_state(self, state_name, publish=True):
        """
        This method should be overridden by specific actuator implementations.

        Parameters:
            state_name (string): the name of the state to set
            publish (boolean): needs the state be published after setting
        """
        if state_name is None:
            return
        print(f"Setting state: {state_name}")
        if state_name in self.states:
            self.state = self.states[state_name]
            self.update_actuator()
            self.publish_current_state()

    def set_value(self, value):
        """
        This method updates the actuator value and triggers the update actuator.
        
        Parameters:
            value (int, float, boolean): the value to set, ON/OFF for switch, duty cycle for light
        """
        if value is not None:
            self.value = value
            self.update_actuator()
            self.publish_brigtness()

    def publish_brigtness(self):
        """
        Publish the current value of the light dim level
        """
        if self.mqtt_client is None:
            print("Mqtt client is not set")
            return
    
        self.mqtt_client.client.publish(self.brightness_state_topic, self.value)
    
    def set_mqtt_client(self, client):
        """
        Add a reference to the mqtt client to send messages from here.

        Parameters:
            client (umqtt.Client): the mqtt client to use for publish and subscribe.
        """
        self.mqtt_client = client

    def add_state(self, state):
        """
        Add a new state to the actuator's states dictionary.
        
        Parameters:
            state (State): the state to add to the list.
        """
        self.states[state.name] = state

    def publish_discovery(self):
        """
        Publish discovery message for the actuator.
        """
        if not self.mqtt_client.client:
            print("MQTT client is not set.")
            return
        
        self.mqtt_client.client.publish(self.discovery_topic, json.dumps(self.discovery_payload), qos=0)
        print(f"Published discovery to {self.discovery_topic}")

    def get_state(self):
        """
        Get the current actuator state.

        Returns:
            State: the current activated state
        """
        return self.state
    
    def publish_current_state(self):
        """
        Publish the current state and value to the MQTT broker.
        """
    
        if not self.mqtt_client.client:
            print("MQTT client is not set.")
            return
        
        if self.state is None:
            print("No state to publish.")
            return
        
        print(f"Publishing state: {self.state_topic} {self.state.name}")
        self.mqtt_client.client.publish(self.state_topic, self.state.name)

    def subscribe_command_topic(self):
        """
        Subscribe to the MQTT command topic.
        """
        if self.mqtt_client.client:
            self.mqtt_client.client.subscribe(self.command_topic)
            self.mqtt_client.add_handler(self)
            print(f"Subscribed to command topic {self.command_topic}")
        else:
            print("MQTT client not set. Cannot subscribe.")

class State:
    """
    Simple state class to hold state name and value.
    """
    def __init__(self, name, value=None):
        """
        The init of the state class

        Parameters:
            name (string): the name of the state
            value (int, fload, boolean): the set value for this state
        """
        self.name = name
        self.value = value