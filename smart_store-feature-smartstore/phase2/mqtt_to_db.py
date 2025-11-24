import os, sys, json, time
from pathlib import Path
import paho.mqtt.client as mqtt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str((PROJECT_ROOT / "phase1").resolve()))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phase1.settings")

import django
django.setup()

from smartstore.models import Fridge
from django.utils import timezone
from email_alerts import send_alert

BROKER = "localhost"
PORT = 1883
TOPICS = ["frig1", "frig2"]

DEFAULT_ALERT_TO = "email address that receive alert"
ALERT_COOLDOWN_SEC = 60
AUTO_OFF_HYST = 0.5

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(" Connected to MQTT broker")
        for t in TOPICS:
            client.subscribe(t)
            print("[mqtt] Subscribed to", t)
    else:
        print(" [mqtt] Connection failed with rc =", rc)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode("utf-8"))
        temp = float(data.get("temperature"))
        hum  = float(data.get("humidity"))
    except Exception as e:
        print(" [parse] Bad payload on", msg.topic, ":", msg.payload, "| err:", e)
        return

    try:
        f = Fridge.objects.get(topic=msg.topic)
        f.temperature = temp
        f.humidity = hum
        f.updated_at = timezone.now()
        f.save(update_fields=["temperature", "humidity", "updated_at"])
        print(f"[db]  Updated {f.name}: {temp}°C, {hum}%")

        try:
            thr= float(f.temp_threshold) if f.temp_threshold is not None else float("inf")
        except Exception:
            thr = float("inf")
        t = float(temp) if temp is not None else -1e9
        if f.fan_on and t <= (thr - AUTO_OFF_HYST):
            try:
                import paho.mqtt.publish as publish
                publish.single(f"fan/{f.topic}/cmd", "OFF", hostname=BROKER, port=PORT, qos=1)
                f.fan_on = False
                f.save(update_fields=["fan_on"])
                print(f"[auto-off] {f.name}: temp {t:.1f} <= {thr - AUTO_OFF_HYST:.1f} -> fan OFF")
            except Exception as e:
                print("[auto-off] publish failed:", e)

        to_addr = f.alert_email or DEFAULT_ALERT_TO
        try:
            thr= float(f.temp_threshold) if f.temp_threshold is not None else float("inf")
        except Exception:
            thr = float("inf")
        t = float(temp) if temp is not None else -1e9
        recent = False
        if f.last_alert_ts:
            recent = (timezone.now() - f.last_alert_ts).total_seconds() < ALERT_COOLDOWN_SEC
        print(f"[alert-check] topic={msg.topic} id={f.id} name={f.name}"
              f"temp={t} thr={thr} to={to_addr} recent={recent}")
        if to_addr and t > thr and not recent:
            try:
                print(f"[email] sending.. {f.name} temp {t} > thr {thr}")
                send_alert(to_addr, f.id, f.name, f.topic, t)
                f.last_alert_ts = timezone.now()
                f.save(update_fields=["last_alert_ts"])
                print(f"[email] sent to {to_addr}")
            except Exception as e:
                print("[email] FAILED:", e)
        else:
            if not to_addr:
                print("[email] skipped: no recipient (set f.alert_email or DEFAULT_ALERT_TO)")
            elif not(t > thr):
                print("[email] skipped: not over threshold")
            elif recent:
                print("[email] skipped: cooldown")
        
      
    except Fridge.DoesNotExist:
        print("[db] No Fridge row for topic:", msg.topic)
def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_forever()
if __name__ == "__main__":
    main()