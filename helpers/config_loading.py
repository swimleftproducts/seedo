import json
import os
from core.seedo.schemas import SeeDoSchema, BrightnessConfigSchema
from core.seedo.registry import SEEDO_REGISTRY, ACTION_REGISTRY

CONFIG_PATH = "data/seedo_config/"

def load_seedo_config(path: str) -> SeeDoSchema:
    with open(path) as f:
        raw = json.load(f)
    schema = SeeDoSchema(**raw)
    return schema


def load_and_build_seedo(path: str):
    schema = load_seedo_config(path)

    seedo_cls = SEEDO_REGISTRY[schema.type]
    action_info = ACTION_REGISTRY[schema.action.type]

    action_schema = action_info["config_schema"]
    action_config = action_schema(**schema.action.params)
    action = action_info["class"](action_config)

    config_schema = seedo_cls.config_schema()
    config = config_schema(**schema.config)

    return seedo_cls.from_schema(schema, config, action)

def load_all_seedos():
    seedos = []
    for filename in os.listdir(CONFIG_PATH):
        if filename.endswith(".json"):
            path = os.path.join(CONFIG_PATH, filename)
            seedo = load_and_build_seedo(path)
            seedos.append(seedo)
    return seedos

def save_seedo(seedo):
    """Save a single SeeDo to a JSON file using its to_dict() method."""

    data = seedo.to_dict()
    
    filename = f"{data['name'].replace(' ', '_').lower()}_demo.json"
    path = os.path.join(CONFIG_PATH, filename)

    with open(path, "w") as f:
         json.dump(data, f, indent=2)

    print(f"Saved SeeDo to {path}")


if __name__ == "__main__":
    # seedo = load_and_build_seedo("data/seedo_config/brightness_test.json")
    # print("---- LOADED SEEDO INSTANCE ----")
    # print("Name:", seedo.name)
    # print("Interval:", seedo.interval_sec)
    # print("Threshold:", seedo.threshold)
    # print("Enabled:", seedo.enabled)

    # print("\nRunning evaluate() using fake frame...")
    # import numpy as np
    # fake_frame = np.ones((100, 100, 3)) * 120  # brightness > threshold
    # result = seedo.evaluate(fake_frame, timestamp=0)
    # print("Evaluate result:", result)


    seedos = load_all_seedos()
    print(f"\n---- LOADED {len(seedos)} SEEDO INSTANCES ----")