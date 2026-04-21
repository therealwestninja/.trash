from pydantic import BaseModel, Field
from typing import Any, Dict, List

class ActionRegistration(BaseModel):
    action_name: str
    description: str = ""
    handler_type: str = "plugin_execute"
    target_plugin: str = ""
    target_action: str = ""
    default_payload: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    policy: Dict[str, Any] = Field(default_factory=dict)

class ActionNameRequest(BaseModel):
    action_name: str

class DispatchRequest(BaseModel):
    action_name: str
    payload_override: Dict[str, Any] = Field(default_factory=dict)

class SetPolicyRequest(BaseModel):
    action_name: str
    policy: Dict[str, Any] = Field(default_factory=dict)
