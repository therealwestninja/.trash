from pydantic import BaseModel, Field
from typing import List

class RegisterHumanRequest(BaseModel):
    human_id: str
    name: str = ""
    tier: str = "public"
    tags: List[str] = Field(default_factory=list)

class ObserveHumanRequest(BaseModel):
    human_id: str
    event: str = "seen"
    closeness_m: float | None = None
    tags: List[str] = Field(default_factory=list)

class UpdateRelationshipRequest(BaseModel):
    human_id: str
    familiarity_delta: float = 0.0
    trust_delta: float = 0.0
    comfort_delta: float = 0.0
    affection_delta: float = 0.0

class RankAttentionRequest(BaseModel):
    visible_human_ids: List[str] = Field(default_factory=list)
