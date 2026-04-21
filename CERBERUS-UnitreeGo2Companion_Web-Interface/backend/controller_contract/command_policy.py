
from typing import List, Dict, Tuple

class CommandPolicy:
    def __init__(self):
        self.allowed_categories: List[str] = ["always"]
        self.restricted: bool = True
        self.reason: str = "System initializing"

    def update(self, state: Dict):
        allowed = ["always"]
        restricted = True
        reason = "Unknown"

        hardware = state.get("hardware", {})
        bridge = state.get("bridge", {})
        session = state.get("session", {})
        safety = state.get("safety", {})

        if safety.get("estop", False):
            self.allowed_categories = ["always"]
            self.restricted = True
            self.reason = "E-STOP ACTIVE"
            return

        if not bridge.get("connected", False):
            self.allowed_categories = ["always"]
            self.restricted = True
            self.reason = "Bridge not connected"
            return

        if not session.get("active", False):
            self.allowed_categories = ["always"]
            self.restricted = True
            self.reason = "No active session"
            return

        mode = hardware.get("mode", "unknown")

        if mode == "simulation":
            allowed = ["motion","behavior","mission","plugin","always"]
            restricted = False
            reason = "Simulation mode"
        elif mode == "real":
            allowed = ["motion","behavior","mission","plugin","body","always"]
            restricted = False
            reason = "Real hardware"
        else:
            allowed = ["always"]
            restricted = True
            reason = "Unknown hardware mode"

        self.allowed_categories = allowed
        self.restricted = restricted
        self.reason = reason

    def is_allowed(self, category: str) -> Tuple[bool,str]:
        if category in self.allowed_categories:
            return True, ""
        return False, f"Category '{category}' not allowed ({self.reason})"

    def to_dict(self):
        return {
            "allowed_categories": self.allowed_categories,
            "restricted": self.restricted,
            "reason": self.reason,
        }
