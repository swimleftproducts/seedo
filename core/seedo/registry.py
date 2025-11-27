from .seedo import BrightnessSeeDo, SemanticSimilaritySeeDo
from .action import EmailAction
from .schemas import EmailActionConfig

SEEDO_REGISTRY = {
    "brightness": BrightnessSeeDo,
    "semantic_similarity": SemanticSimilaritySeeDo
}

ACTION_REGISTRY = {
    "email": {
      "class": EmailAction,
      "config_schema": EmailActionConfig
    }
}
