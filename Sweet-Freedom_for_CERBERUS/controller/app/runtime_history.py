from __future__ import annotations

from time import time
from typing import Any


def append_history_entry(
    history: list[dict[str, Any]],
    *,
    text: str,
    goal: dict | None,
    feedback: dict | None,
    result: dict | None,
    action: dict | None,
    motion_state: str,
    control_source: str,
    degraded: bool,
    lifecycle: dict | None,
    limit: int = 30,
) -> list[dict[str, Any]]:
    entry = {
        "timestamp": time(),
        "text": text,
        "goal": goal,
        "feedback": feedback,
        "result": result,
        "action": action,
        "motion_state": motion_state,
        "control_source": control_source,
        "degraded": degraded,
        "lifecycle": lifecycle,
    }
    history.insert(0, entry)
    del history[limit:]
    return history
