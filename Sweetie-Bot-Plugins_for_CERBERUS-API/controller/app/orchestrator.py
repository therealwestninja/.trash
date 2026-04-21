from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from app.plugin_registry import PluginRegistry
from app.state_store import StateStore
from app.trace_logger import TraceLogger


PIPELINE: List[str] = [
    "attention.select_focus",
    "social.rank_targets",
    "mood.update",
    "mission.plan",
    "behavior.select",
    "expression.compose",
]


@dataclass
class Orchestrator:
    registry: PluginRegistry = field(default_factory=PluginRegistry)
    state_store: StateStore = field(default_factory=StateStore)
    traces: TraceLogger = field(default_factory=TraceLogger)

    def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        session_id = event.get("session_id", "default")
        state = self.state_store.load(session_id)
        trace = {"session_id": session_id, "steps": []}

        for action in PIPELINE:
            trace["steps"].append({"action": action, "status": "planned"})

        self.state_store.save(session_id, state)
        self.traces.record(trace)
        return {
            "ok": True,
            "session_id": session_id,
            "pipeline": PIPELINE,
            "state": state,
            "note": "Controller skeleton only. Wire plugin endpoints and state merge logic next.",
        }
