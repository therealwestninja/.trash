from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class Vec3(BaseModel):
    x: float
    y: float
    z: float = 0.0

class WorldObject(BaseModel):
    id: str
    label: str
    category: str = "unknown"
    frame: str = "map"
    position: Vec3
    confidence: float = 1.0
    attributes: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    ttl_seconds: Optional[int] = None

class ObservationBatch(BaseModel):
    source: str = "unknown"
    objects: List[WorldObject] = Field(default_factory=list)

class QueryNearRequest(BaseModel):
    origin: Vec3
    radius_m: float = 2.0
    labels: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)

class GetObjectRequest(BaseModel):
    id: str

class DeleteObjectRequest(BaseModel):
    id: str
