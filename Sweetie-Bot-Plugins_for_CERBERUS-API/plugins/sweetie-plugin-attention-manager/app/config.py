import os
from dataclasses import dataclass
@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME","sweetie-plugin-attention-manager")
    plugin_version: str = os.getenv("PLUGIN_VERSION","2.0.0")
    novelty_weight: float = float(os.getenv("DEFAULT_NOVELTY_WEIGHT","0.30"))
    social_weight: float = float(os.getenv("DEFAULT_SOCIAL_WEIGHT","0.40"))
    salience_weight: float = float(os.getenv("DEFAULT_SALIENCE_WEIGHT","0.30"))
    bonding_url: str = os.getenv("BONDING_URL","http://localhost:7000")
    autonomy_url: str = os.getenv("AUTONOMY_URL","http://localhost:7000")
settings = Settings()
