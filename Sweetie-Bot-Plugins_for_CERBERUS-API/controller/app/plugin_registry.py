from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Dict


@dataclass
class PluginRegistry:
    endpoints_path: Path = Path("plugins/configs/plugin-endpoints.json")
    endpoints: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.endpoints_path.exists():
            self.endpoints = json.loads(self.endpoints_path.read_text(encoding="utf-8"))
