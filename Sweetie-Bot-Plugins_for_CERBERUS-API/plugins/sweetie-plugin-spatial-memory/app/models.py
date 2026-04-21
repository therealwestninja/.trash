from pydantic import BaseModel, Field
from typing import Dict, Any

class RememberLocationRequest(BaseModel):
    name: str
    position: Dict[str, float]
    confidence: float = 0.7
    metadata: Dict[str, Any] = Field(default_factory=dict)

class UpdatePositionRequest(BaseModel):
    position: Dict[str, float]

class GetNearbyRequest(BaseModel):
    radius: float = 2.0
