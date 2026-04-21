from typing import List
from pydantic import BaseModel, Field

class AttentionCandidate(BaseModel):
    target_id: str
    label: str
    confidence: float = 0.5
    tags: List[str] = Field(default_factory=list)
    distance_m: float = 0.0
    novelty: float = 0.0
    salience: float = 0.5
    persistence: float = 0.0
    relationship_tier: str | None = None
    target_kind: str = "entity"

class IngestCandidatesRequest(BaseModel):
    candidates: List[AttentionCandidate] = Field(default_factory=list)

class SetBiasRequest(BaseModel):
    novelty_weight: float | None = None
    social_weight: float | None = None
    salience_weight: float | None = None
