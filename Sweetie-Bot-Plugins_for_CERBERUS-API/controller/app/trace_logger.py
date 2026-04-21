from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class TraceLogger:
    traces: List[Dict[str, Any]] = field(default_factory=list)

    def record(self, trace: Dict[str, Any]) -> None:
        self.traces.append(trace)
