from typing import Dict, Any
from pydantic import BaseModel

class ExecuteRequest(BaseModel):
    type: str
    payload: Dict[str, Any] = {}

class PluginResponse(BaseModel):
    ok: bool = True
    plugin: str
    action: str
    data: Dict[str, Any] = {}
