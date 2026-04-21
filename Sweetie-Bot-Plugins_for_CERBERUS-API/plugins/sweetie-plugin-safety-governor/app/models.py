from pydantic import BaseModel, Field
from typing import Dict, Any

class EvaluateActionRequest(BaseModel):
    action: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)

class SetPolicyRequest(BaseModel):
    max_speed_mps: float | None = None
    public_min_distance_m: float | None = None
    supporting_min_distance_m: float | None = None
    best_friend_min_distance_m: float | None = None
    low_battery_threshold: float | None = None

class ReportContextRequest(BaseModel):
    context: Dict[str, Any] = Field(default_factory=dict)
