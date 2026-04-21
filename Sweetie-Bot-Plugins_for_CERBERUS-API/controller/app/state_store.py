from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class StateStore:
    sessions: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def load(self, session_id: str) -> Dict[str, Any]:
        return self.sessions.setdefault(session_id, {})

    def save(self, session_id: str, state: Dict[str, Any]) -> None:
        self.sessions[session_id] = state
