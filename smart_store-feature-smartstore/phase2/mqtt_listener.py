import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC1 = "frig1"
TOPIC2 = "frig2"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to broker {BROKER}")
        client.subscribe(TOPIC1)
        client.subscribe(TOPIC2)
        print(f"Subscribed to topic {TOPIC1}, {TOPIC2}")
    else:
        print("Connection failed")

def on_message(client, userdata, msg):
    print(f"\nMessage received on topic {msg.topic}")
    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)

        temperature = data.get("temperature")
        humidity = data.get("humidity")

        print(f"Temperature: {temperature}°C | Humidity: {humidity}%")


    except json.JSONDecodeError:
        print("Received non-JSON message:", msg.payload)

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, keepalive=60)
client.loop_forever()