from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class TranslateRequest(BaseModel):
    action: str
    direction: Optional[str] = None
    speed: float = 0.2
    duration: float = 0.0
    posture: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SequencePayload(BaseModel):
    commands: List[Dict[str, Any]] = Field(default_factory=list)
