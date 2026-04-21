from dataclasses import dataclass, field
from datetime import datetime, UTC
import os

CERBERUS_API_BASE_URL = os.getenv("CERBERUS_API_BASE_URL", "http://host.docker.internal:8000")

def now_iso():
    return datetime.now(UTC).isoformat()

@dataclass
class State:
    last_motion_request: dict | None = None
    translated_count: int = 0

state = State()

def translate_motion(payload: dict):
    env = {
        "translated_at": now_iso(),
        "cerberus_api_base_url": CERBERUS_API_BASE_URL,
        "motion_command": {
            "kind": payload.get("kind", "locomotion"),
            "speed_mps": payload.get("speed_mps", 0.6),
            "heading_rad": payload.get("heading_rad", 0.0),
            "gait": payload.get("gait", "walk"),
            "movement_profile": payload.get("movement_profile", "canine")
        },
        "status": "stub_translated"
    }
    state.last_motion_request = env
    state.translated_count += 1
    return env

def report_state():
    return {"translated_count": state.translated_count, "last_motion_request": state.last_motion_request}
