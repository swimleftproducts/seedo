from pydantic import BaseModel
from typing import Dict, Any

class ActionSchema(BaseModel):
    type: str
    params: Dict[str, Any]

class EmailActionConfig(BaseModel):
    to: str
    from_: str  # can't use "from" keyword in Python
    subject: str
    body_template: str


class BrightnessConfigSchema(BaseModel):
    threshold: float

class SeeDoSchema(BaseModel):
    type: str
    name: str
    interval_sec: float
    enabled: bool = True
    config: Dict[str, Any]
    action: ActionSchema
