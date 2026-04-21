from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ExecuteRequest(BaseModel):
    type: str = Field(..., description="Action type, such as robot.command or ros2.publish")
    payload: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)

class ExecuteResponse(BaseModel):
    ok: bool = True
    plugin: str
    action: str
    data: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)

class PluginManifest(BaseModel):
    name: str
    version: str
    api_version: str
    description: str
    capabilities: List[str]
    entrypoints: Dict[str, str]

class HealthResponse(BaseModel):
    status: str
    plugin: str
    version: str
