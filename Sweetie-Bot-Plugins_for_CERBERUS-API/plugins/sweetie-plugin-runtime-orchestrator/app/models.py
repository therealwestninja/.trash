from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class RegisterRoutesRequest(BaseModel):
    safety_url: str | None = None
    navigation_url: str | None = None
    docking_url: str | None = None
    bonding_url: str | None = None
    crusader_url: str | None = None
    autonomy_url: str | None = None

class PatrolMissionRequest(BaseModel):
    waypoints: List[Dict[str, float]] = Field(default_factory=list)
    loop: bool = False

class ChainExecuteRequest(BaseModel):
    chain_name: str
    payload: Dict[str, Any] = Field(default_factory=dict)
