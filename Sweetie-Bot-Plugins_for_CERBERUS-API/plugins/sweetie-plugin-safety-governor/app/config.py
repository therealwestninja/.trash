import os
from dataclasses import dataclass
@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME", "sweetie-plugin-safety-governor")
    plugin_version: str = os.getenv("PLUGIN_VERSION", "2.0.0")
    max_speed_mps: float = float(os.getenv("DEFAULT_MAX_SPEED_MPS", "1.2"))
    public_min_distance_m: float = float(os.getenv("DEFAULT_PUBLIC_MIN_DISTANCE_M", "0.9"))
    supporting_min_distance_m: float = float(os.getenv("DEFAULT_SUPPORTING_MIN_DISTANCE_M", "0.75"))
    best_friend_min_distance_m: float = float(os.getenv("DEFAULT_BEST_FRIEND_MIN_DISTANCE_M", "0.45"))
    low_battery_threshold: float = float(os.getenv("DEFAULT_LOW_BATTERY_THRESHOLD", "0.2"))
settings = Settings()
