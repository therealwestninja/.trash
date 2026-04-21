from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ProcessIntentRequest(BaseModel):
    intent: str
    context: Dict[str, Any] = Field(default_factory=dict)

class GenerateStyleRequest(BaseModel):
    action_name: str
    context: Dict[str, Any] = Field(default_factory=dict)

class SetPersonaStateRequest(BaseModel):
    energy: Optional[float] = None
    curiosity: Optional[float] = None
    affection: Optional[float] = None
    drama: Optional[float] = None
    caution: Optional[float] = None
    notes: List[str] = Field(default_factory=list)
