import time
from PIL import Image
import numpy as np
from abc import ABC, abstractmethod
import threading
import os
from typing import List


from torch import embedding
from .action import Action
from .schemas import SeeDoSchema, BrightnessConfigSchema, ActionSchema, SemanticSimilarityConfigSchema, SemanticRegion

EMBEDDING_SAVE_FOLDER_BASE = 'data/seedo_config'
IMAGE_SAVE_FOLDER_BASE = 'data/seedo_config'

class SeeDo:
    def __init__(self, name, interval_sec, min_retrigger_interval_sec, action: Action, enabled=True):
        self.name = name
        self.interval_sec = interval_sec
        self.min_retrigger_interval_sec = min_retrigger_interval_sec
        #TODO maybe support multiple actions
        self.action = action
        self.enabled = enabled
        # This is the timestamp of last eval run
        self._last_run = 0.0

        # This is the timestamp of last time the action was executed
        self._last_action_time = 0.0

        self._action_lock = threading.Lock()   # <--- lock for safe update

    def toggle_enabled(self):
        print(f'Toggling {self.name} to {(not self.enabled)}')
        self.enabled = not self.enabled

    def should_run(self, now):
        return (now - self._last_run) >= self.interval_sec

    def mark_ran(self, now):
        self._last_run = now

    def do(self, context):
        self.action.execute(context)

    @abstractmethod
    def evaluate(self, frame, timestamp) -> bool:
        """Override in subclass to evaluate condition"""
        pass

  
    
    @classmethod
    @abstractmethod
    def config_schema(cls):
        """Return the matching Pydantic config schema class."""
        pass

    @abstractmethod
    def to_dict(self):
        """Used for saving the the seedo"""
        pass

    @classmethod
    @abstractmethod
    def from_schema(cls, schema: SeeDoSchema, config, action):
        """Instantiate from schema & config"""
        pass
    
class SemanticSimilaritySeeDo(SeeDo):
    """A seedo that compares semantic similarity of regions in the frame to reference embeddings."""
    def __init__(self, name, interval_sec, min_retrigger_interval_sec, semantic_regions: List[SemanticSimilarityConfigSchema], action, enabled=True):
        super().__init__(name, interval_sec, min_retrigger_interval_sec, action, enabled)
        self.semantic_regions = semantic_regions  # List of dicts with roi and embedding
        

    def evaluate(self, frame, timestamp, ml_manager) -> bool:
        if frame is None:
            return False

        images = []
        for region in self.semantic_regions:
            x1, y1, x2, y2 = region.roi
            pil = Image.fromarray(frame)
            cropped = pil.crop((x1, y1, x2, y2))
            images.append(cropped)

        # Compute embeddings batch
        new_embeddings = ml_manager.mobile_net_v3.get_embedding_batch(images)

        # check thresholds individually
        triggered = False
        for region, current_emb in zip(self.semantic_regions, new_embeddings):
            sim = ml_manager.mobile_net_v3.cosine_similarity_matrix(
                np.vstack([region.embedding.squeeze(), current_emb.squeeze()])
            )[0,1]

            if region.greater_than and sim > region.similarity_threshold:
                triggered = True
            elif not region.greater_than and sim < region.similarity_threshold:
                triggered = True

        return triggered


    

    @classmethod
    def build_embedding_save_path(cls, seedo_name: str, index: int) -> str:
        return os.path.join(EMBEDDING_SAVE_FOLDER_BASE, seedo_name, f"embedding_{index}.npy")

    @classmethod
    def build_roi_image_save_path(cls, seedo_name: str, index: int) -> str:
        return os.path.join(IMAGE_SAVE_FOLDER_BASE, seedo_name, f"roi_image_{index}.png")

    @classmethod
    def save_roi_embedding_to_file(cls, seedo_name: str, index:int, embedding: np.ndarray):
        """Save embedding to .npy file."""
        filepath = cls.build_embedding_save_path(seedo_name, index)
        #create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        np.save(filepath, embedding)
        return filepath
    
    @classmethod
    def save_roi_image_to_file(cls, seedo_name: str, image: Image.Image, index:int):
        """Save image to file."""
        filepath = cls.build_roi_image_save_path(seedo_name, index)
        #create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        image.save(filepath)
        return filepath
    
    @classmethod
    def config_schema(cls):
        """Return the matching Pydantic config schema class."""
        return SemanticSimilarityConfigSchema

    def to_dict(self):
        regions = []
        for idx, region in enumerate(self.semantic_regions):
            regions.append({
                "roi": region.roi,
                "image_path": self.build_roi_image_save_path(self.name, idx),
                "embedding_path": self.build_embedding_save_path(self.name, idx),
                "similarity_threshold": region.similarity_threshold,
                "greater_than": region.greater_than,
            })

        return {
            "type": "semantic_similarity",
            "name": self.name,
            "interval_sec": self.interval_sec,
            "min_retrigger_interval_sec": self.min_retrigger_interval_sec,
            "enabled": self.enabled,
            "config": {
                "semantic_regions": [r.model_dump(exclude={"image", "embedding"}) for r in self.semantic_regions]
            },
            "action": self.action.to_dict()
        }


    @classmethod
    def from_schema(cls, schema: SeeDoSchema, config: SemanticSimilarityConfigSchema, action):
        """Instantiate from schema & config"""

        # Load images and embeddings for each semantic region
        semantic_regions = []
        for region in config.semantic_regions:
            # Load image & embedding files
            image = Image.open(region.image_path)
            embedding = np.load(region.embedding_path)

            # Assign runtime-only fields (not serialized)
            region.image = image
            region.embedding = embedding

            semantic_regions.append(region)

        return cls(
            name=schema.name,
            interval_sec=schema.interval_sec,
            min_retrigger_interval_sec=schema.min_retrigger_interval_sec,
            semantic_regions=semantic_regions,
            action=action,
            enabled=schema.enabled
        )
    


class BrightnessSeeDo(SeeDo):
    def __init__(self, name, interval_sec, min_retrigger_interval_sec, threshold, action, enabled=True):
        super().__init__(name, interval_sec, min_retrigger_interval_sec, action, enabled)
        self.threshold = threshold

    @classmethod
    def config_schema(cls):
        return BrightnessConfigSchema

    def evaluate(self, frame, timestamp, ml_manager):
        if frame is None:
            return False
        brightness = frame.mean()
        print(f"[{self.name}] brightness={brightness}")
        if self.threshold < 0:
            return brightness < -self.threshold
        return brightness > self.threshold

    @classmethod
    def from_schema(cls, schema: SeeDoSchema, config: BrightnessConfigSchema, action):
        return cls(
            name=schema.name,
            interval_sec=schema.interval_sec,
            min_retrigger_interval_sec=schema.min_retrigger_interval_sec,
            threshold=config.threshold,
            action=action,
            enabled=schema.enabled
        )
    
    def to_dict(self):
        schema = SeeDoSchema(
        type="brightness",
        name=self.name,
        interval_sec=self.interval_sec,
        min_retrigger_interval_sec=self.min_retrigger_interval_sec,
        enabled=self.enabled,
        config=BrightnessConfigSchema(threshold=self.threshold).model_dump(),
        action=self.action.to_dict()
        )
        return schema.model_dump()