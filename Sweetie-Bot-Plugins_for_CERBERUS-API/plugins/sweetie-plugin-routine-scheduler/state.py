from dataclasses import dataclass, field
import time

@dataclass
class Routine:
    name: str
    interval: float
    last_run: float = 0

@dataclass
class State:
    routines: dict = field(default_factory=dict)

state = State()
