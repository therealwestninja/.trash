from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class EpisodeIngestRequest(BaseModel):
    text: str
    tags: List[str] = Field(default_factory=list)
    salience: float = 0.5
    relationship_tier: Optional[str] = None
    autonomy_mode: Optional[str] = None

class LocationIngestRequest(BaseModel):
    name: str
    position: Dict[str, float] = Field(default_factory=dict)
    confidence: float = 0.5
    metadata: Dict[str, str] = Field(default_factory=dict)

class BehaviorOutcomeIngestRequest(BaseModel):
    behavior: str
    reward: float = 0.0
    outcome: str = "unknown"
    tags: List[str] = Field(default_factory=list)
    relationship_tier: Optional[str] = None
    autonomy_mode: Optional[str] = None
