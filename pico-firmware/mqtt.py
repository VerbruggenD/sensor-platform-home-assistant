import os
import time
import json
from umqtt.simple import MQTTClient
import credentials

# MQTT Broker settings
broker_address = credentials.broker_address
broker_port = credentials.broker_port
username = credentials.username
password = credentials.password

class MQTTHandler:
    def __init__(self, client_id):
        """
        Initialize the MQTT client.

        Parameters:
            client_id (str): The unique client ID for the MQTT connection.
        """
        self.client = MQTTClient(client_id, broker_address, port=broker_port, user=username, password=password, keepalive=120)
        self.client.set_callback(self.on_message)
        self.config_handler = None
        self.handlers = []
        self.connect()
    
    def connect(self):
        """
        Connect to the MQTT broker with retry mechanism.
        """
        while True:
            try:
                self.client.connect()
                print("Successfully connected to MQTT Broker.")
                break
            except Exception as e:
                print(f"Failed to connect to MQTT broker: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    def reconnect(self):
        """
        Reconnect to the MQTT broker with retry mechanism.
        """
        try:
            self.client.connect()
            print("Successfully connected to MQTT Broker.")
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}. Retrying in 60 seconds...")
            time.sleep(60)

    def subscribe(self, topic):
        """
        Subscribe to a specific MQTT topic.

        Parameters:
            topic (str): The MQTT topic to subscribe to.
        """
        self.client.subscribe(topic)
        print(f"Subscribed to {topic}")

    def set_config_handler(self, config_handler):
        """
        Set the configuration handler.

        Parameters:
            config_handler (object): The configuration handler object.
        """
        self.config_handler = config_handler
        print("config handler set")

    def check_messages(self):
        """
        Check for incoming MQTT messages.
        """
        self.client.check_msg()  # Non-blocking call to check messages

    def add_handler(self, handler):
        """
        Add a message handler to the list.

        Parameters:
            handler (object): The handler object with an on_message method.
        """
        self.handlers.append(handler)
        print(f"Added handler {handler} to list")

    def on_message(self, topic, msg):
        """
        Callback function to handle incoming MQTT messages.

        Parameters:
            topic (bytes): The topic of the incoming message.
            msg (bytes): The payload of the incoming message.
        """
        print(f"Received message from {topic}: {msg}")
        topic = topic.decode()
        msg = msg.decode()

        # Delegate the message handling to the config handler if it's set
        if self.config_handler and topic == "general/config_response":
            self.config_handler.handle_config(msg)

        # Handle heartbeat requests
        elif topic.startswith("heartbeat/"):
            self.handle_heartbeat(topic)

        else:
            for handler in self.handlers:
                handler.on_message(topic, msg)

    def handle_heartbeat(self, topic):
        """
        Handle heartbeat requests and send responses.

        Parameters:
            topic (str): The topic of the heartbeat request.
        """
        # Respond to heartbeat requests
        response_topic = "heartbeat/response"
        response_message = topic.split("/")[1]  # Extract client_id from the topic
        print(f"response msg {response_message}")
        self.client.publish(response_topic, response_message, qos = 0)
        print(f"Heartbeat response sent: {response_message} to {response_topic}")

    def check_connection(self):
        """
        Check if the MQTT client is connected.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self.client.is_connected()