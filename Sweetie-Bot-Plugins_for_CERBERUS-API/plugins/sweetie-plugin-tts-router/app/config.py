import os
from dataclasses import dataclass
@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME","sweetie-plugin-tts-router")
    plugin_version: str = os.getenv("PLUGIN_VERSION","2.0.0")
    default_provider: str = os.getenv("DEFAULT_PROVIDER","mock")
    default_voice: str = os.getenv("DEFAULT_VOICE","sweetie_bright")
    default_rate: float = float(os.getenv("DEFAULT_RATE","1.08"))
    default_pitch: float = float(os.getenv("DEFAULT_PITCH","1.12"))
settings = Settings()
