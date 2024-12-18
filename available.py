import paho.mqtt.client as mqtt
import json
import time

# MQTT broker details
MQTT_BROKER = "production-docker.local"
MQTT_PORT = 1883
MQTT_USERNAME = "dieter"
MQTT_PASSWORD = "dieter"

# Device details
AVAILABILITY_TOPIC = f"room-dieter/28-cd-c1-0d-6d-28-space-heater/availability"

# Initialize MQTT client
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Connect to MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Send availability message
client.loop_start()

try:
    client.publish(AVAILABILITY_TOPIC, "online", retain=True)
    print("Send availability")
except KeyboardInterrupt:
    print("Exiting...")
finally:
    # Announce device as unavailable before exiting
    # client.publish(AVAILABILITY_TOPIC, "offline", retain=True)
    client.loop_stop()
    client.disconnect()