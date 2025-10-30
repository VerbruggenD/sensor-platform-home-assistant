from enum import Enum
import logging

logger = logging.getLogger('my_logger')

class State(Enum):
    """
    Device states for heartbeat monitoring.
    """
    ONLINE = 1
    DISRUPTED = 2
    OFFLINE = 3
    DISABLED = 4

class DeviceHeartbeat:
    def __init__(self, macAddress, sensors, actuators, state, mqtt_client):
        """
        Initialize a DeviceHeartbeat instance.

        Parameters:
            macAddress (str): The MAC address of the device.
            sensors (list): List of sensors associated with the device.
            actuators (list): List of actuators associated with the device.
            state (State): Initial state of the device.
        """
        self.macAddress = macAddress
        self.state = state
        self.sensors = sensors
        self.actuators = actuators
        self.mqtt_client = mqtt_client

    def publish_availability(self, availability):
        """
        Publish the availability status to MQTT topics for all sensors and actuators.

        Parameters:
            availability (str): The availability status ("online" or "offline").
        """
        try:
            for sensor in self.sensors:
                topic = f"{sensor['room']}/{self.macAddress}-{sensor['name']}/availability"
                self.mqtt_client.publish(topic, payload=availability, qos=0)
                logger.info(f"Published '{availability}' to {topic}")
            for actuator in self.actuators:
                topic = f"{actuator['room']}/{self.macAddress}-{actuator['name']}/availability"
                self.mqtt_client.publish(topic, payload=availability, qos=0)
                logger.info(f"Published '{availability}' to {topic}")
        except Exception as e:
            logger.error(f"Failed to publish availability for {self.macAddress}: {e}")

    def handleBadPing(self):
        """
        Handle a bad ping (no response) from the device.
        """
        if self.state == State.DISRUPTED:
            self.state = State.OFFLINE
            self.publish_availability("offline")
        elif self.state == State.ONLINE:
            self.state = State.DISRUPTED

    def handleGoodPing(self):
        """
        Handle a good ping (response) from the device.
        """
        if self.state == State.DISABLED:
            return
        if self.state != State.ONLINE:
            self.state = State.ONLINE
            self.publish_availability("online")

    def handleNewPing(self, result):
        """
        Process a new ping result.
        
        Parameters:
            result (bool): True if the ping was successful, False otherwise.
        """
        if self.state == State.DISABLED:
            return
        if not result:
            self.handleBadPing()
        else:
            self.handleGoodPing()