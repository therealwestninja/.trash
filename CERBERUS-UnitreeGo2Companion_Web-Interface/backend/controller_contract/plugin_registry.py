from __future__ import annotations

from dataclasses import dataclass, field

from .models import PluginFeatureState


@dataclass
class PluginRecord:
    name: str
    enabled: bool = True
    features: list[str] = field(default_factory=list)
    health: str = 'healthy'

    def to_model(self) -> PluginFeatureState:
        return PluginFeatureState(enabled=self.enabled, features=self.features, health=self.health)


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, PluginRecord] = {
            'sweetie_bot': PluginRecord(
                name='sweetie_bot',
                enabled=True,
                features=['autonomy', 'social', 'peer', 'dock', 'memory'],
            )
        }

    def get_capabilities(self) -> dict[str, PluginFeatureState]:
        return {name: record.to_model() for name, record in self._plugins.items()}

    def set_health(self, name: str, health: str) -> None:
        if name in self._plugins:
            self._plugins[name].health = health
