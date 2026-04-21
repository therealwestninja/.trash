import os
from dataclasses import dataclass
@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME","sweetie-plugin-stt-router")
    plugin_version: str = os.getenv("PLUGIN_VERSION","2.0.0")
    default_provider: str = os.getenv("DEFAULT_PROVIDER","mock")
    default_language: str = os.getenv("DEFAULT_LANGUAGE","en")
    default_mode: str = os.getenv("DEFAULT_MODE","command_and_chat")
settings = Settings()
