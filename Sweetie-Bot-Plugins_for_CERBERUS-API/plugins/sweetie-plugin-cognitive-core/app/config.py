import os
from dataclasses import dataclass
@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME", "sweetie-plugin-cognitive-core")
    plugin_version: str = os.getenv("PLUGIN_VERSION", "2.0.0")
    memory_url: str = os.getenv("MEMORY_URL", "http://localhost:7000")
    event_bus_url: str = os.getenv("EVENT_BUS_URL", "http://localhost:7000")
    attention_url: str = os.getenv("ATTENTION_URL", "http://localhost:7000")
    bonding_url: str = os.getenv("BONDING_URL", "http://localhost:7000")
    behavior_url: str = os.getenv("BEHAVIOR_URL", "http://localhost:7000")
    safety_url: str = os.getenv("SAFETY_URL", "http://localhost:7000")
    autonomy_url: str = os.getenv("AUTONOMY_URL", "http://localhost:7000")
settings = Settings()
