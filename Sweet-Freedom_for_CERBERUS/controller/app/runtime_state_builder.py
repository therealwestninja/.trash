from __future__ import annotations

from typing import Any

from .diagnostics import build_diagnostics_snapshot


def build_runtime_state_payload(
    *,
    base_state: dict[str, Any],
    motion_state: str,
    command_history: list[dict[str, Any]],
    active_goal: dict | None,
    last_feedback: dict | None,
    goal_result: dict | None,
    session: dict,
    command_mux: dict,
    lifecycle: dict,
    recording: dict,
    is_degraded: bool,
) -> dict[str, Any]:
    state = dict(base_state)
    state["telemetry"] = {
        "motion_state": motion_state,
        "command_count": len(command_history),
        "last_command_at": command_history[0]["timestamp"] if command_history else None,
    }
    state["command_history"] = command_history
    state["active_goal"] = active_goal
    state["last_feedback"] = last_feedback
    state["goal_result"] = goal_result
    state["session"] = session
    state["command_mux"] = command_mux
    state["lifecycle"] = lifecycle
    state["diagnostics"] = build_diagnostics_snapshot(runtime_state=state)
    state["diagnostics"]["summary"]["degraded"] = is_degraded
    state["recording"] = recording
    return state
