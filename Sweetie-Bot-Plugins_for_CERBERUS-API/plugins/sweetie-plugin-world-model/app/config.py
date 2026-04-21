import os
from dataclasses import dataclass

@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME", "sweetie-plugin-world-model")
    plugin_version: str = os.getenv("PLUGIN_VERSION", "1.0.0")
    default_frame: str = os.getenv("DEFAULT_FRAME", "map")
    default_ttl_seconds: int = int(os.getenv("DEFAULT_TTL_SECONDS", "600"))

settings = Settings()
