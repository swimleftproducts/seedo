import time
from abc import ABC, abstractmethod
import threading
from .action import Action
from .schemas import SeeDoSchema, BrightnessConfigSchema, ActionSchema

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
    def from_config(cls, config: dict):
        """Instantiate SeeDo from config dictionary"""
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
    

class BrightnessSeeDo(SeeDo):
    def __init__(self, name, interval_sec, min_retrigger_interval_sec, threshold, action, enabled=True):
        super().__init__(name, interval_sec, min_retrigger_interval_sec, action, enabled)
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