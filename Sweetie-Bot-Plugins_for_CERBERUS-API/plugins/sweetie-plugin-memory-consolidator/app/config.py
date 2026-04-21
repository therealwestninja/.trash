import os
from dataclasses import dataclass
@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME","sweetie-plugin-memory-consolidator")
    plugin_version: str = os.getenv("PLUGIN_VERSION","2.0.0")
    min_observations: int = int(os.getenv("DEFAULT_MIN_OBSERVATIONS","2"))
    location_confidence_bonus: float = float(os.getenv("DEFAULT_LOCATION_CONFIDENCE_BONUS","0.10"))
    behavior_confidence_bonus: float = float(os.getenv("DEFAULT_BEHAVIOR_CONFIDENCE_BONUS","0.12"))
settings = Settings()
