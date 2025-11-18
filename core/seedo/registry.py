from .seedo import BrightnessSeeDo
from .action import EmailAction, EmailActionConfig

SEEDO_REGISTRY = {
    "brightness": BrightnessSeeDo
}

ACTION_REGISTRY = {
    "email": {
      "class": EmailAction,
      "config_schema": EmailActionConfig
    }
}
