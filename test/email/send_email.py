import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

# Load .env file into environment
load_dotenv()

EMAIL_ADDRESS = 'swimleft@gmail.com'
APP_PW = os.getenv("APP_PW")

msg = MIMEText("This is the body of the message")
msg["Subject"] = "Hello from Pi"
msg["From"] = EMAIL_ADDRESS
msg["To"] = "13038875015@txt.att.net"

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(EMAIL_ADDRESS, APP_PW)
    server.send_message(msg)

print("Email sent successfully!")
