from abc import ABC, abstractmethod
from .schemas import EmailActionConfig

class Action(ABC):
    @abstractmethod
    def execute(self, context: dict):
        """
        Perform the action. 'context' may contain frame, timestamp, etc., message, 
        """
        pass


class EmailAction(Action):
    def __init__(self, config: EmailActionConfig ):
        self.to = config.to
        self.from_ = config.from_
        self.subject = config.subject
        self.body_template = config.body_template


    def execute(self, context):
        print(f"[EmailAction] Sending email: {self.subject}")