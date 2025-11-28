from abc import ABC, abstractmethod
from pydantic import BaseModel
from core.seedo.schemas import EmailActionConfig
import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class Action(ABC):
    @abstractmethod
    def execute(self, context: dict):
        """
        Perform the action. 'context' may contain frame, timestamp, etc., message, 
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """Return a dictionary representation of the action for saving to config."""
        pass

class EmailAction(Action):
    def __init__(self, config: EmailActionConfig ):
        self.type_string = 'email'
        self.to = config.to
        self.from_ = config.from_
        self.subject = config.subject
        self.body_template = config.body_template

        self.app_pw = os.getenv("APP_PW")


    def execute(self, context):
        video_file = context['saved_file_path']
        print(f"[EmailAction] Sending email: {self.subject}")
        # Create multipart message
        msg = MIMEMultipart()
        msg["Subject"] = self.subject
        msg["From"] = self.from_
        msg["To"] = self.to

        msg.attach(MIMEText(f'{self.body_template}', "plain"))

        # Add video attachment
        with open(video_file, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{os.path.basename(video_file)}"'
        )

        msg.attach(part)

        # Send
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(self.from_, self.app_pw)
            server.send_message(msg)

        print("Email sent successfully!")


    
    def to_dict(self):
        return {
            "type": self.type_string,
            "params": EmailActionConfig(
                to=self.to,
                from_=self.from_,
                subject=self.subject,
                body_template=self.body_template
            ).model_dump()
        }
    




