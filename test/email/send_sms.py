import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load password from environment variable
load_dotenv()

APP_PW = os.getenv("APP_PW")

if not APP_PW:
    raise ValueError("Environment variable APP_PW is not set!")

SMS_RECIPIENT = "3038875015@sms.clicksend.com"
SMTP_USER = "swimleft@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_sms(message: str):
    msg = MIMEText(message)
    msg["From"] = SMTP_USER
    msg["To"] = SMS_RECIPIENT
    msg["Subject"] = ""  # SMS gateways don't need a subject

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, APP_PW)
        server.sendmail(SMTP_USER, SMS_RECIPIENT, msg.as_string())

# Example usage
send_sms("Camera event detected.")
