from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass
class Settings:
    cerberus_api_url: str = os.getenv("CERBERUS_API_URL", "http://localhost:8000")
    unitree_mode: str = os.getenv("UNITREE_MODE", "go2")
    timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))

settings = Settings()
