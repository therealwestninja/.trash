import os
from dataclasses import dataclass
@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME", "sweetie-plugin-social-bonding")
    plugin_version: str = os.getenv("PLUGIN_VERSION", "1.0.0")
    max_supporting_humans: int = int(os.getenv("MAX_SUPPORTING_HUMANS", "6"))
    default_stranger_decay: float = float(os.getenv("DEFAULT_STRANGER_DECAY", "0.05"))
    default_supporting_decay: float = float(os.getenv("DEFAULT_SUPPORTING_DECAY", "0.02"))
    default_best_friend_decay: float = float(os.getenv("DEFAULT_BEST_FRIEND_DECAY", "0.005"))
settings = Settings()
