import os
from dataclasses import dataclass
@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME","sweetie-plugin-behavior-engine")
    plugin_version: str = os.getenv("PLUGIN_VERSION","2.0.0")
settings = Settings()
