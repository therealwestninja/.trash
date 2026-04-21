import os
from dataclasses import dataclass

@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME", "sweetie-plugin-action-registry")
    plugin_version: str = os.getenv("PLUGIN_VERSION", "1.0.0")

settings = Settings()
