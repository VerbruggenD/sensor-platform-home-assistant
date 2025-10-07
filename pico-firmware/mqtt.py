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
        self.client = MQTTClient(client_id, broker_address, port=broker_port, user=username, password=password, keepalive=120)
        self.client.set_callback(self.on_message)
        self.config_handler = None
        self.handlers = []
        self.connect()
    
    def connect(self):
        while True:
            try:
                self.client.connect()
                print("Successfully connected to MQTT Broker.")
                break
            except Exception as e:
                print(f"Failed to connect to MQTT broker: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    def reconnect(self):
        try:
            self.client.connect()
            print("Successfully connected to MQTT Broker.")
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}. Retrying in 60 seconds...")
            time.sleep(60)

    def subscribe(self, topic):
        self.client.subscribe(topic)
        print(f"Subscribed to {topic}")

    def set_config_handler(self, config_handler):
        self.config_handler = config_handler
        print("config handler set")

    def check_messages(self):
        self.client.check_msg()  # Non-blocking call to check messages

    def add_handler(self, handler):
        self.handlers.append(handler)
        print(f"Added handler {handler} to list")

    def on_message(self, topic, msg):
        print(f"Received message from {topic}: {msg}")
        topic = topic.decode()
        msg = msg.decode()

        # Delegate the message handling to the config handler if it's set
        if self.config_handler and topic == "general/config_response":
            self.config_handler.handle_config(topic, msg)

        # Handle heartbeat requests
        elif topic.startswith("heartbeat/"):
            self.handle_heartbeat(topic, msg)

        else:
            for handler in self.handlers:
                handler.on_message(topic, msg)

    def handle_heartbeat(self, topic, msg):
        # Respond to heartbeat requests
        response_topic = "heartbeat/response"
        response_message = topic.split("/")[1]  # Extract client_id from the topic
        print(f"response msg {response_message}")
        self.client.publish(response_topic, response_message, qos = 0)
        print(f"Heartbeat response sent: {response_message} to {response_topic}")

    def check_connection(self):
        return self.client.is_connected()