from typing import List, Optional
from pydantic import BaseModel, Field

class RecordOutcomeRequest(BaseModel):
    behavior: str
    outcome: str = "unknown"
    reward: float = 0.0
    tags: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
    relationship_tier: Optional[str] = None
    autonomy_mode: Optional[str] = None

class AdjustTraitsRequest(BaseModel):
    curiosity: Optional[float] = None
    caution: Optional[float] = None
    affection: Optional[float] = None
    confidence: Optional[float] = None
