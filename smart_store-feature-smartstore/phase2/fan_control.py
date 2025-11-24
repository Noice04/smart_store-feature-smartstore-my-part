import os
import time
import json
import paho.mqtt.client as mqtt

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)


BROKER = "localhost"
PORT   = 1883
FAN_PINS = {}  

# Load pins from json 
# json content: {"frig1":18, "frig2":23}
PINMAP_FILE = os.path.join(os.path.dirname(__file__), "fan_pins.json")
if os.path.exists(PINMAP_FILE):
    FAN_PINS = json.load(open(PINMAP_FILE))

def ensure_pin(topic):
    pin = FAN_PINS.get(topic, 18)  # default 18
    GPIO.setup(pin, GPIO.OUT)
    return pin

def set_pin(topic, on):
    pin = ensure_pin(topic)
    GPIO.output(pin, GPIO.HIGH if on else GPIO.LOW)

def on_connect(c, u, f, rc):
    print("Fan control connected.", rc)
    for topic in FAN_PINS.keys():
        c.subscribe(f"fan/{topic}/cmd")

def on_message(c, u, msg):
    topic = msg.topic.split("/")[1] 
    cmd = msg.payload.decode().strip().upper()
    if cmd in ("ON","OFF"):
        set_pin(topic, cmd=="ON")
        c.publish(f"fan/{topic}/status", cmd, retain=True)
        print(f"[fan] {topic} -> {cmd}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
try:
    client.loop_forever()
finally:
    GPIO.cleanup()
