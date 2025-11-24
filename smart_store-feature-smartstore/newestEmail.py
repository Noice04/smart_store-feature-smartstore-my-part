import time
import json
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from gpiozero import Motor
import paho.mqtt.client as mqtt

# MQTT
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPICS_SENSOR = ["Frig1", "Frig2"]
TOPIC_FAN_CONTROL = "FanControl1"
TOPIC_FAN_STATUS = "FanStatus1"

# Temperature thresholds 
THRESHOLDS = {
    "Frig1": 10,  # °C
    "Frig2": 12
}

# Gmail settings
EMAIL_USER = "youremail@gmail.com"
APP_PASSWORD = "your_app_password_here"
RECEIVER_EMAIL = "receiver@gmail.com"
IMAP_SERVER = "imap.gmail.com"

# GPIO motor setup
MOTOR_PIN_FORWARD = 17
MOTOR_PIN_BACKWARD = 27
fan = Motor(forward=MOTOR_PIN_FORWARD, backward=MOTOR_PIN_BACKWARD)

# State tracking
last_alert_time = {"Frig1": 0, "Frig2": 0}
alert_cooldown = 60  # seconds before sending another alert

# EMAIL FUNCTIONS
def send_email(fridge, temperature):
    subject = f"⚠️ Temperature Alert - {fridge}"
    body = f"""
    The current temperature for {fridge} is {temperature}°C.
    Would you like to turn on the fan?
    Please reply with 'YES' to activate the fan.
    """

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[EMAIL SENT] Alert for {fridge}: {temperature}°C")
    except Exception as e:
        print(f"[ERROR] Could not send email: {e}")

def check_email_for_yes():
    """Check inbox for YES replies."""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, APP_PASSWORD)
    mail.select("inbox")

    status, messages = mail.search(None, '(UNSEEN SUBJECT "Temperature Alert")')

    if status == "OK":
        for num in messages[0].split():
            typ, data = mail.fetch(num, "(RFC822)")
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Decode email body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode()
            else:
                body = msg.get_payload(decode=True).decode()

            if "YES" in body.upper():
                print("✅ YES reply detected — turning fan ON!")
                turn_fan_on()

            mail.store(num, '+FLAGS', '\\Seen')

    mail.logout()

# ======================================================
# FAN CONTROL
# ======================================================
def turn_fan_on():
    fan.forward()
    mqtt_client.publish(TOPIC_FAN_STATUS, "ON")
    print("🌀 Fan ON")

def turn_fan_off():
    fan.stop()
    mqtt_client.publish(TOPIC_FAN_STATUS, "OFF")
    print("🛑 Fan OFF")

# ======================================================
# MQTT HANDLING
# ======================================================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker.")
        for t in TOPICS_SENSOR:
            client.subscribe(t)
            print(f"📡 Subscribed to topic: {t}")
        client.subscribe(TOPIC_FAN_CONTROL)
    else:
        print("❌ MQTT connection failed.")

def on_message(client, userdata, msg):
    topic = msg.topic
    message = msg.payload.decode()
    print(f"[MQTT] {topic} → {message}")

    # Fan command topic
    if topic == TOPIC_FAN_CONTROL:
        if message.upper() == "ON":
            turn_fan_on()
        elif message.upper() == "OFF":
            turn_fan_off()
        return

    # Temperature sensor topics
    try:
        data = json.loads(message)
        temperature = float(data.get("temperature", 0))
    except:
        temperature = float(message)

    if temperature > THRESHOLDS[topic]:
        now = time.time()
        if now - last_alert_time[topic] > alert_cooldown:
            send_email(topic, temperature)
            last_alert_time[topic] = now
        else:
            print(f"⏳ Cooldown active for {topic}")
    else:
        # Optional: auto turn off fan when temp drops
        turn_fan_off()

# ======================================================
# MAIN PROGRAM LOOP
# ======================================================
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

try:
    mqtt_client.loop_start()
    print("🚀 Smart Store System Running... (Press Ctrl+C to exit)")
    while True:
        check_email_for_yes()
        time.sleep(30)
except KeyboardInterrupt: 
    print("\n🧹 Cleaning up...")
    fan.stop()
    mqtt_client.loop_stop()
    
