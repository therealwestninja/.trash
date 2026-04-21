from __future__ import annotations


QUICK_ACTION_TEXT = {
    "greet": "hello sweetie",
    "stop": "stop",
    "look": "look around",
    "explore": "explore the area",
    "follow": "follow me",
    "move_forward": "move forward",
}


def resolve_quick_action(action: str) -> str:
    normalized = (action or "").strip().lower()
    return QUICK_ACTION_TEXT.get(normalized, normalized.replace("_", " "))
