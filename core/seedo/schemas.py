from pydantic import BaseModel, Field
from typing import Dict, Any, Tuple, List, Optional
from PIL import Image
import numpy as np

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

    # Runtime-only fields (not part of saved JSON)
    image: Optional[Image.Image] = Field(default=None, exclude=True)
    embedding: Optional[np.ndarray] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True   # Required to support Image & numpy types


class SemanticSimilarityConfigSchema(BaseModel):
    semantic_regions: List[SemanticRegion]
