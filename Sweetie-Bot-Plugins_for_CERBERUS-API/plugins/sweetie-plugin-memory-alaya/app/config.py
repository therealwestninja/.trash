import os
from dataclasses import dataclass

@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME", "sweetie-plugin-memory-alaya")
    plugin_version: str = os.getenv("PLUGIN_VERSION", "2.0.0")
    decay_per_day: float = float(os.getenv("DEFAULT_DECAY_PER_DAY", "0.04"))

settings = Settings()
