from pydantic import BaseModel, Field
from typing import Dict, Any

class RoutineAddRequest(BaseModel):
    name: str
    interval: float
    suggested_action: Dict[str, Any] = Field(default_factory=dict)
