import os
from dataclasses import dataclass
@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME","sweetie-plugin-event-bus")
    plugin_version: str = os.getenv("PLUGIN_VERSION","2.1.0")
    max_recent_events: int = int(os.getenv("MAX_RECENT_EVENTS","250"))
settings = Settings()
