import os
from dataclasses import dataclass

@dataclass
class Settings:
    plugin_name: str = os.getenv("PLUGIN_NAME", "sweetie-plugin-sim-learn")
    plugin_version: str = os.getenv("PLUGIN_VERSION", "1.0.0")
    default_dataset_dir: str = os.getenv("DEFAULT_DATASET_DIR", "/tmp/sweetie-sim-learn")

settings = Settings()
