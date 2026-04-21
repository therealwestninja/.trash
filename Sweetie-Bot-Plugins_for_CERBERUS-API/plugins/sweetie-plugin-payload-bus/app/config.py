import os
from dataclasses import dataclass

@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME", "sweetie-plugin-payload-bus")
    plugin_version: str = os.getenv("PLUGIN_VERSION", "1.0.0")
    default_heartbeat_ttl_seconds: int = int(os.getenv("DEFAULT_HEARTBEAT_TTL_SECONDS", "300"))

settings = Settings()
