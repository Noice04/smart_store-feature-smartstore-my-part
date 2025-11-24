import time, imaplib, email, re
import paho.mqtt.client as mqtt
from email.header import decode_header, make_header
import os, sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent   
PROJECT_DIR = BASE_DIR / "phase1"
sys.path.insert(0, str(PROJECT_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phase1.settings")
import django
django.setup()

from smartstore.models import Fridge

GMAIL_ADDRESS = "email that read reply"
APP_PASSWORD  = ""

BROKER = "localhost"
PORT   = 1883

client = mqtt.Client()
client.connect(BROKER, PORT, 60)
client.loop_start()

def _plain(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type()=="text/plain":
                try:
                    return part.get_content().strip()
                except Exception:
                    return part.get_payload(decode=True).decode(errors="ignore")
        return ""
    else:
        try:
            return msg.get_content().strip()
        except Exception:
            return msg.get_payload(decode=True).decode(errors="ignore")

def watch():
    M = imaplib.IMAP4_SSL("imap.gmail.com")
    M.login(GMAIL_ADDRESS, APP_PASSWORD)
    M.select("INBOX")
    # unseen only
    typ, data = M.search(None, 'UNSEEN')
    ids = data[0].split()
    for i in ids:
        typ, msg_data = M.fetch(i, "(RFC822)")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)
        body = _plain(msg).upper()
        # find FID:<id>
        m = re.search(r'FID\s*:\s*(\d+)', body)
        if "YES" in body and m:
            fid = int(m.group(1))
            try:
                f = Fridge.objects.get(pk=fid)
                client.publish(f"fan/{f.topic}/cmd", "ON", qos=1)
                f.fan_on = True
                f.save(update_fields=["fan_on"])
                print(f"[email] YES for fridge {f.name} -> fan ON")
            except Fridge.DoesNotExist:
                print("[email] FID not found:", fid)
    M.close(); M.logout()

if __name__ == "__main__":
    try:
        while True:
            watch()
            time.sleep(20)
    finally:
        client.loop_stop()
