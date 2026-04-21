from __future__ import annotations

from time import time
from typing import Any


def build_diagnostics_snapshot(*, runtime_state: dict[str, Any]) -> dict[str, Any]:
    safety = runtime_state.get("safety", {})
    session = runtime_state.get("session", {})
    telemetry = runtime_state.get("telemetry", {})
    goal = runtime_state.get("active_goal", {})
    result = runtime_state.get("goal_result", {})
    mux = runtime_state.get("command_mux", {})

    return {
        "timestamp": time(),
        "summary": {
            "motion_state": telemetry.get("motion_state"),
            "armed": safety.get("armed"),
            "estop_active": safety.get("estop_active"),
            "active_source": mux.get("active_source"),
            "session_active": session.get("active"),
            "session_degraded": session.get("degraded"),
            "active_goal": goal.get("action_type"),
            "goal_status": result.get("status"),
        },
        "safety": safety,
        "session": session,
        "telemetry": telemetry,
        "goal": goal,
        "goal_result": result,
        "command_mux": mux,
    }
