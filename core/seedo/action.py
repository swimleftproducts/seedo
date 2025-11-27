from abc import ABC, abstractmethod
from pydantic import BaseModel
from core.seedo.schemas import EmailActionConfig

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


    def execute(self, context):
        print(f"[EmailAction] Sending email: {self.subject}")
    
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