import os
from dataclasses import dataclass

@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME", "sweetie-plugin-docking-behavior")
    plugin_version: str = os.getenv("PLUGIN_VERSION", "1.0.0")
    alignment_tolerance_m: float = float(os.getenv("DEFAULT_ALIGNMENT_TOLERANCE_M", "0.20"))
    dock_approach_distance_m: float = float(os.getenv("DEFAULT_DOCK_APPROACH_DISTANCE_M", "1.00"))
    low_battery_threshold: float = float(os.getenv("DEFAULT_LOW_BATTERY_THRESHOLD", "0.20"))

settings = Settings()
