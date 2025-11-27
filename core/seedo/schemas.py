from pydantic import BaseModel
from typing import Dict, Any, Tuple, List

class ActionSchema(BaseModel):
    type: str
    params: Dict[str, Any]

class EmailActionConfig(BaseModel):
    to: str
    from_: str  # can't use "from" keyword in Python
    subject: str
    body_template: str

class SeeDoSchema(BaseModel):
    type: str
    name: str
    interval_sec: float
    min_retrigger_interval_sec: float = 0.0
    enabled: bool = True
    config: Dict[str, Any]
    action: ActionSchema

class BrightnessConfigSchema(BaseModel):
    threshold: float

class SemanticRegion(BaseModel):
    roi: Tuple[int, int, int, int]
    embedding_path: str       # reference to .npy file
    image_path: str           # cropped ROI image
    similarity_threshold: float
    greater_than: bool = True

class SemanticSimilarityConfigSchema(BaseModel):
    semantic_regions: List[SemanticRegion]
