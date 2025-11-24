
import smtplib, imaplib, email, re, time
from email.message import EmailMessage

GMAIL_ADDRESS = "email that read reply"
APP_PASSWORD  = "" 

def send_alert(to_addr, fridge_id, fridge_name, topic, temp):
    subject = f"[ALERT] Fridge {fridge_name} (id={fridge_id}) @ {temp:.1f}°C"
    body = (
        f"Fridge {fridge_name} (topic: {topic}) is {temp:.1f} °C, above threshold.\n"
        f"Reply YES to turn the fan ON.\n"
        f"Include the token: FID:{fridge_id}\n"
    )
    msg = EmailMessage()
    msg["From"] = GMAIL_ADDRESS
    msg["To"]   = to_addr
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(GMAIL_ADDRESS, APP_PASSWORD)
            smtp.send_message(msg)
            print(f"[email] sent to {to_addr}")
    except Exception as e:
        print("[email] Failed:", e)