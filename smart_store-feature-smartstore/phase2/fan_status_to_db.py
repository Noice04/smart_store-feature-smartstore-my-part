import django, os, sys
from pathlib import Path
import paho.mqtt.client as mqtt

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phase1.settings")
django.setup()

from smartstore.models import Fridge

BROKER="localhost"; PORT=1883

def on_message(c,u,msg):
    topic = msg.topic.split("/")[1]
    state = msg.payload.decode().strip().upper() == "ON"
    try:
        f = Fridge.objects.get(topic=topic)
        if f.fan_on != state:
            f.fan_on = state
            f.save(update_fields=["fan_on"])
            print(f"[status] {f.name} fan_on={state}")
    except Fridge.DoesNotExist:
        pass

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.subscribe("fan/+/status")
client.loop_forever()
