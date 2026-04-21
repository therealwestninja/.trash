from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SessionContext(BaseModel):
    session_id: str
    conversation_id: Optional[str] = None
    actor_id: Optional[str] = None
    environment_id: Optional[str] = None


class RequestContext(BaseModel):
    trace_id: Optional[str] = None
    user_id: Optional[str] = None
    priority: Optional[str] = None
    mode: Optional[str] = None


class RequestPolicy(BaseModel):
    dry_run: bool = False
    timeout_ms: int = 1200
    safe_mode: bool = True


class ExecuteRequest(BaseModel):
    request_id: str
    timestamp: str
    source: str
    plugin: str
    action: str
    session: SessionContext
    context: RequestContext = Field(default_factory=RequestContext)
    state: Dict[str, Any] = Field(default_factory=dict)
    input: Dict[str, Any] = Field(default_factory=dict)
    policy: RequestPolicy = Field(default_factory=RequestPolicy)


class PluginEvent(BaseModel):
    event_id: str
    type: str
    source_plugin: str
    timestamp: str
    session_id: str
    data: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    visibility: str = "internal"


class PluginCommand(BaseModel):
    command_id: str
    type: str
    target: str
    priority: str = "normal"
    data: Dict[str, Any] = Field(default_factory=dict)


class PluginError(BaseModel):
    code: str
    message: str
    retryable: bool = False
    details: Dict[str, Any] = Field(default_factory=dict)


class ExecuteResponse(BaseModel):
    ok: bool = True
    request_id: str
    plugin: str
    action: str
    version: str
    result: Dict[str, Any] = Field(default_factory=dict)
    state_patch: Dict[str, Any] = Field(default_factory=dict)
    events: List[PluginEvent] = Field(default_factory=list)
    commands: List[PluginCommand] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errors: List[PluginError] = Field(default_factory=list)
