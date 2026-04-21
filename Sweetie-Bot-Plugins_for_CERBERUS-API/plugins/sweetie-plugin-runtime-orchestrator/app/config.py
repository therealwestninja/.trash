import os
from dataclasses import dataclass
@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME", "sweetie-plugin-runtime-orchestrator")
    plugin_version: str = os.getenv("PLUGIN_VERSION", "2.0.0")
    safety_url: str = os.getenv("SAFETY_URL", "http://localhost:7000")
    navigation_url: str = os.getenv("NAVIGATION_URL", "http://localhost:7000")
    docking_url: str = os.getenv("DOCKING_URL", "http://localhost:7000")
    bonding_url: str = os.getenv("BONDING_URL", "http://localhost:7000")
    crusader_url: str = os.getenv("CRUSADER_URL", "http://localhost:7000")
    autonomy_url: str = os.getenv("AUTONOMY_URL", "http://localhost:7000")
settings = Settings()
