import os
from dataclasses import dataclass
@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME","sweetie-plugin-learning-loop")
    plugin_version: str = os.getenv("PLUGIN_VERSION","2.0.0")
    learning_rate: float = float(os.getenv("DEFAULT_LEARNING_RATE","0.10"))
    decay_rate: float = float(os.getenv("DEFAULT_DECAY_RATE","0.01"))
settings = Settings()
