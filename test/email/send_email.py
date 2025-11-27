import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

load_dotenv()

EMAIL_ADDRESS = "swimleft@gmail.com"
APP_PW = os.getenv("APP_PW")

VIDEO_FILE = "data/camera_1763681027_1763681029.avi"

# Create multipart message
msg = MIMEMultipart()
msg["Subject"] = "Hello from Pi"
msg["From"] = EMAIL_ADDRESS
msg["To"] = "13038875015@txt.att.net"

# Add text body
msg.attach(MIMEText("This is the body of the message", "plain"))

# Add video attachment
with open(VIDEO_FILE, "rb") as f:
    part = MIMEBase("application", "octet-stream")
    part.set_payload(f.read())

encoders.encode_base64(part)
part.add_header(
    "Content-Disposition",
    f'attachment; filename="{os.path.basename(VIDEO_FILE)}"'
)

msg.attach(part)

# Send
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(EMAIL_ADDRESS, APP_PW)
    server.send_message(msg)

print("Email sent successfully!")
