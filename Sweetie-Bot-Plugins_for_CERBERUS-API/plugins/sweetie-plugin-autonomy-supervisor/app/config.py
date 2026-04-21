import os
from dataclasses import dataclass

def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}

@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME", "sweetie-plugin-autonomy-supervisor")
    plugin_version: str = os.getenv("PLUGIN_VERSION", "1.0.0")
    low_battery: float = float(os.getenv("DEFAULT_LOW_BATTERY", "0.20"))
    critical_battery: float = float(os.getenv("DEFAULT_CRITICAL_BATTERY", "0.10"))
    idle_timeout_sec: int = int(os.getenv("DEFAULT_IDLE_TIMEOUT_SEC", "300"))
    social_window_sec: int = int(os.getenv("DEFAULT_SOCIAL_WINDOW_SEC", "90"))
    exploration_enabled: bool = _bool("DEFAULT_EXPLORATION_ENABLED", True)

settings = Settings()
