from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Capability:
    id: str
    title: str
    category: str
    source: str
    description: str
    modes: list[str]
    inputs: list[str]
    outputs: list[str]
    safety_level: str = "standard"
    enabled: bool = True
    tags: list[str] | None = None


class CapabilityRegistry:
    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}
        self._seed_defaults()

    def _seed_defaults(self) -> None:
        defaults = [
            Capability(
                id="movement.basic",
                title="Basic Movement",
                category="movement",
                source="core",
                description="High-level movement actions like move forward, stop, and follow.",
                modes=["manual", "ai"],
                inputs=["text", "quick_action"],
                outputs=["goal", "feedback", "result"],
                safety_level="movement",
                tags=["core", "motion"],
            ),
            Capability(
                id="safety.control",
                title="Safety Control",
                category="safety",
                source="core",
                description="Arm, disarm, and E-Stop control surface.",
                modes=["manual", "diagnostics"],
                inputs=["ui", "api"],
                outputs=["safety_state"],
                safety_level="critical",
                tags=["core", "safety"],
            ),
            Capability(
                id="diagnostics.observe",
                title="Diagnostics",
                category="diagnostics",
                source="core",
                description="Runtime diagnostics, event visibility, and health summaries.",
                modes=["diagnostics"],
                inputs=["api"],
                outputs=["diagnostics", "events"],
                safety_level="readonly",
                tags=["core", "observability"],
            ),
            Capability(
                id="recording.session",
                title="Session Recording",
                category="tooling",
                source="core",
                description="Record, export, and replay runtime sessions as JSONL.",
                modes=["diagnostics", "simulation"],
                inputs=["api", "ui"],
                outputs=["recording", "replay"],
                safety_level="readonly",
                tags=["recording", "replay"],
            ),
            Capability(
                id="autonomy.placeholder",
                title="Autonomy Hook",
                category="autonomy",
                source="planned",
                description="Reserved slot for future planner/autonomy providers.",
                modes=["ai"],
                inputs=["planner_goal"],
                outputs=["goal", "feedback", "result"],
                safety_level="movement",
                enabled=False,
                tags=["planned", "autonomy"],
            ),
            Capability(
                id="animation.placeholder",
                title="Animation Engine Hook",
                category="animation",
                source="planned",
                description="Reserved slot for future FunScript and animation providers.",
                modes=["animation"],
                inputs=["script", "timeline"],
                outputs=["animation_state"],
                safety_level="movement",
                enabled=False,
                tags=["planned", "animation"],
            ),
        ]
        for capability in defaults:
            self._capabilities[capability.id] = capability

    def list_capabilities(self) -> list[dict[str, Any]]:
        return [asdict(capability) for capability in self._capabilities.values()]

    def get_capability(self, capability_id: str) -> dict[str, Any] | None:
        capability = self._capabilities.get(capability_id)
        return None if capability is None else asdict(capability)

    def snapshot(self) -> dict[str, Any]:
        capabilities = self.list_capabilities()
        categories = sorted({item["category"] for item in capabilities})
        return {
            "count": len(capabilities),
            "categories": categories,
            "capabilities": capabilities,
        }


capability_registry = CapabilityRegistry()
