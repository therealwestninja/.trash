import os
from dataclasses import dataclass
@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME", "sweetie-plugin-interaction-core")
    plugin_version: str = os.getenv("PLUGIN_VERSION", "2.0.0")
    bonding_url: str = os.getenv("BONDING_URL", "http://localhost:7000")
    behavior_url: str = os.getenv("BEHAVIOR_URL", "http://localhost:7000")
    tts_url: str = os.getenv("TTS_URL", "http://localhost:7000")
settings = Settings()
