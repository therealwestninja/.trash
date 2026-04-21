import os
from dataclasses import dataclass

@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME", "sweetie-plugin-crusader-link")
    plugin_version: str = os.getenv("PLUGIN_VERSION", "1.0.0")
    max_peers: int = int(os.getenv("MAX_PEERS", "2"))
    link_priority: list[str] = tuple((os.getenv("LINK_PRIORITY","bluetooth,wifi,voice").split(",")))

settings = Settings()
