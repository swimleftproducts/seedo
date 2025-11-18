import time
from abc import ABC, abstractmethod
from .action import Action
from .schemas import SeeDoSchema, BrightnessConfigSchema

class SeeDo:
    def __init__(self, name, interval_sec, action: Action, enabled=True):
        self.name = name
        self.interval_sec = interval_sec
        #TODO maybe support multiple actions
        self.action = action
        self.enabled = enabled
        self._last_run = 0.0

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
    def from_config(cls, config: dict):
        """Instantiate SeeDo from config dictionary"""
        pass
    
    @classmethod
    @abstractmethod
    def config_schema(cls):
        """Return the matching Pydantic config schema class."""
        pass
    

class BrightnessSeeDo(SeeDo):
    def __init__(self, name, interval_sec, threshold, action, enabled=True):
        super().__init__(name, interval_sec, action, enabled)
        self.threshold = threshold

    @classmethod
    def config_schema(cls):
        return BrightnessConfigSchema

    def evaluate(self, frame, timestamp):
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
            threshold=config.threshold,
            action=action,
            enabled=schema.enabled
        )

