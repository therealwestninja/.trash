from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ReportContextRequest(BaseModel):
    battery: float = 1.0
    safety_blocked: bool = False
    operator_visible: bool = False
    best_friend_visible: bool = False
    supporting_visible: bool = False
    public_present: bool = False
    peer_online: bool = False
    social_target_visible: bool = False
    routine_triggered: List[str] = Field(default_factory=list)
    dock_known: bool = False
    charging: bool = False
    current_mode: Optional[str] = None
    current_goal: Optional[str] = None
    current_position: Dict[str, float] = Field(default_factory=lambda: {"x":0.0,"y":0.0})

class TransitionRequest(BaseModel):
    from_mode: str
    to_mode: str
    reason: str = ""

class SetPolicyRequest(BaseModel):
    low_battery: Optional[float] = None
    critical_battery: Optional[float] = None
    idle_timeout_sec: Optional[int] = None
    social_window_sec: Optional[int] = None
    exploration_enabled: Optional[bool] = None
