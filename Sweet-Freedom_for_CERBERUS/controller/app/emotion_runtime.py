from dataclasses import dataclass, field
from typing import Any


@dataclass
class EmotionRuntime:
    snapshot: dict[str, float] = field(
        default_factory=lambda: {"valence": 0.5, "stress": 0.2, "curiosity": 0.4}
    )
    history: list[dict[str, Any]] = field(default_factory=list)

    def process_text(self, text: str) -> dict[str, float]:
        cleaned = text.strip().lower()
        delta_valence = 0.0
        delta_stress = 0.0
        delta_curiosity = 0.0

        if any(word in cleaned for word in ["good", "great", "nice", "thanks", "happy"]):
            delta_valence += 0.1
        if any(word in cleaned for word in ["danger", "error", "stop", "fail", "panic"]):
            delta_stress += 0.25
            delta_valence -= 0.1
        if any(word in cleaned for word in ["why", "how", "what", "explore", "look", "search"]):
            delta_curiosity += 0.15

        self.snapshot["valence"] = min(1.0, max(0.0, self.snapshot["valence"] + delta_valence))
        self.snapshot["stress"] = min(1.0, max(0.0, self.snapshot["stress"] + delta_stress))
        self.snapshot["curiosity"] = min(1.0, max(0.0, self.snapshot["curiosity"] + delta_curiosity))

        result = dict(self.snapshot)
        self.history.append({"text": text, "snapshot": result})
        return result
