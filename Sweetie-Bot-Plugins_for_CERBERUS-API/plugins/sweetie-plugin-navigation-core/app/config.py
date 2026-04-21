import os
from dataclasses import dataclass

@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME", "sweetie-plugin-navigation-core")
    plugin_version: str = os.getenv("PLUGIN_VERSION", "1.0.0")
    default_step_size_m: float = float(os.getenv("DEFAULT_STEP_SIZE_M", "0.5"))
    default_goal_tolerance_m: float = float(os.getenv("DEFAULT_GOAL_TOLERANCE_M", "0.25"))

settings = Settings()
