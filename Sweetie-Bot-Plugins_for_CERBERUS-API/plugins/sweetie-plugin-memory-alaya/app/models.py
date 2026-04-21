from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class StoreMemoryRequest(BaseModel):
    text: str
    tags: List[str] = Field(default_factory=list)
    source: str = "unknown"
    salience: float = 0.5
    metadata: Dict[str, Any] = Field(default_factory=dict)
    relationship_tier: Optional[str] = None
    ttl_days: Optional[int] = None

class QueryMemoryRequest(BaseModel):
    text: str
    limit: int = 5
    tags: List[str] = Field(default_factory=list)
    preferred_relationship_tiers: List[str] = Field(default_factory=list)

class ConsolidateRequest(BaseModel):
    min_tag_overlap: int = 2

class IdRequest(BaseModel):
    id: str
