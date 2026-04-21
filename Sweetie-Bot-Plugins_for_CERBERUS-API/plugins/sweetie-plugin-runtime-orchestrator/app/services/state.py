from dataclasses import dataclass, field
from app.config import settings

@dataclass
class State:
    routes: dict = field(default_factory=lambda: {
        "safety": settings.safety_url,
        "navigation": settings.navigation_url,
        "docking": settings.docking_url,
        "bonding": settings.bonding_url,
        "crusader": settings.crusader_url,
        "autonomy": settings.autonomy_url,
    })
    history: list[dict] = field(default_factory=list)

state = State()
