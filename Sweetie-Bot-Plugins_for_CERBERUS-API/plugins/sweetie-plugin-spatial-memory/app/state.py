from dataclasses import dataclass, field

@dataclass
class SpatialState:
    position: dict = field(default_factory=lambda: {"x":0,"y":0})
    locations: dict = field(default_factory=dict)

state = SpatialState()
