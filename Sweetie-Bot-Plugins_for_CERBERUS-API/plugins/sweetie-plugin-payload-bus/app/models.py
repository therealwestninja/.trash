from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class PayloadDescriptor(BaseModel):
    id: str
    name: str
    kind: str = "service"
    version: str = "1.0.0"
    base_url: str
    health_url: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    heartbeat_ttl_seconds: Optional[int] = None

class CapabilityRequest(BaseModel):
    capability: str

class RouteRequest(BaseModel):
    capability: str
    request: Dict[str, Any] = Field(default_factory=dict)
    preferred_payload_id: Optional[str] = None

class PayloadIdRequest(BaseModel):
    id: str
