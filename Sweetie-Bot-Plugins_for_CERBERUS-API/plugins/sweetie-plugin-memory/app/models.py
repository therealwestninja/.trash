from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExecuteRequest(BaseModel):
    type: str = Field(..., description="Command type or capability route.")
    payload: Dict[str, Any] = Field(default_factory=dict)


class PluginManifest(BaseModel):
    name: str
    version: str
    api_version: str = "1"
    capabilities: List[str]
    direct_controller_ready: bool = True
    cerberus_api_ready: bool = True
    docs_path: str = "/docs"


class ErrorResponse(BaseModel):
    ok: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None

class MemoryStoreRequest(BaseModel):
    session_id: str
    namespace: str = "default"
    key: str
    value: Any


class MemoryLookupRequest(BaseModel):
    session_id: str
    namespace: str = "default"
    key: str


class MemoryDeleteRequest(BaseModel):
    session_id: str
    namespace: str = "default"
    key: str
