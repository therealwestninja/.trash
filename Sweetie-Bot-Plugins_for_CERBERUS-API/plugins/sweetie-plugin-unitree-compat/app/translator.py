from __future__ import annotations
from typing import Any, Dict, List

POSTURE_PRESETS = {
    "greet": {"action": "stand", "body_pose": "upright", "head": "track_user"},
    "crouch": {"action": "stand", "body_pose": "low", "speed_limit": 0.1},
    "observe": {"action": "stand", "body_pose": "neutral", "head": "scan"},
    "neutral": {"action": "stop", "body_pose": "neutral"},
}

MOTION_PRESETS = {
    "patrol_step": [
        {"action": "walk", "direction": "forward", "speed": 0.25, "duration": 1.5},
        {"action": "turn", "direction": "left", "speed": 0.2, "duration": 0.8},
    ],
    "sidestep_left": [
        {"action": "strafe", "direction": "left", "speed": 0.2, "duration": 1.0},
    ],
    "sidestep_right": [
        {"action": "strafe", "direction": "right", "speed": 0.2, "duration": 1.0},
    ],
    "turn_scan": [
        {"action": "turn", "direction": "left", "speed": 0.18, "duration": 1.0},
        {"action": "turn", "direction": "right", "speed": 0.18, "duration": 2.0},
        {"action": "turn", "direction": "left", "speed": 0.18, "duration": 1.0},
    ],
}


def _vector_for_direction(direction: str | None) -> Dict[str, float]:
    direction = (direction or "forward").lower()
    mapping = {
        "forward": {"vx": 1.0, "vy": 0.0, "wz": 0.0},
        "backward": {"vx": -1.0, "vy": 0.0, "wz": 0.0},
        "left": {"vx": 0.0, "vy": 1.0, "wz": 0.0},
        "right": {"vx": 0.0, "vy": -1.0, "wz": 0.0},
    }
    return mapping.get(direction, mapping["forward"])


def translate_command(command: Dict[str, Any]) -> Dict[str, Any]:
    action = (command.get("action") or "stop").lower()
    speed = float(command.get("speed", 0.2))
    duration = float(command.get("duration", 0.0))
    direction = command.get("direction")

    if action in {"stand", "sit", "stop"}:
        return {
            "backend_action": action,
            "mode": "high_level",
            "duration": duration,
            "metadata": command.get("metadata", {}),
        }

    if action == "walk":
        vec = _vector_for_direction(direction)
        return {
            "backend_action": "velocity_move",
            "mode": "high_level",
            "vx": vec["vx"] * speed,
            "vy": vec["vy"] * speed,
            "wz": 0.0,
            "duration": duration,
        }

    if action == "strafe":
        vec = _vector_for_direction(direction)
        return {
            "backend_action": "velocity_move",
            "mode": "high_level",
            "vx": 0.0,
            "vy": vec["vy"] * speed,
            "wz": 0.0,
            "duration": duration,
        }

    if action == "turn":
        sign = 1.0 if (direction or "left").lower() == "left" else -1.0
        return {
            "backend_action": "velocity_move",
            "mode": "high_level",
            "vx": 0.0,
            "vy": 0.0,
            "wz": sign * speed,
            "duration": duration,
        }

    return {
        "backend_action": action,
        "mode": "passthrough",
        "raw": command,
        "warning": "Unknown action passed through without normalization.",
    }
