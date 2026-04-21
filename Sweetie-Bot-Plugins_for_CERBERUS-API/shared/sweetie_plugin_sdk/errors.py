from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class SweetieError(Exception):
    code: str
    message: str
    retryable: bool = False
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
            "details": self.details,
        }
