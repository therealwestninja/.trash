import os
from dataclasses import dataclass

def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME", "sweetie-plugin-nav2-pathing")
    plugin_version: str = os.getenv("PLUGIN_VERSION", "1.0.0")
    cerberus_api_url: str = os.getenv("CERBERUS_API_URL", "http://localhost:8000")
    ros2_bridge_url: str = os.getenv("ROS2_BRIDGE_URL", "http://localhost:7010")
    forward_to_ros2: bool = _to_bool(os.getenv("FORWARD_TO_ROS2"), False)
    default_frame: str = os.getenv("DEFAULT_FRAME", "map")
    max_speed_mps: float = float(os.getenv("MAX_SPEED_MPS", "0.8"))

settings = Settings()
