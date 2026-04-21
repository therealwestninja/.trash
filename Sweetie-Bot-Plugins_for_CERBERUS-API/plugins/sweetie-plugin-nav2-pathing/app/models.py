from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class Point2D(BaseModel):
    x: float
    y: float

class Pose2D(Point2D):
    yaw: float = 0.0

class NavPreviewRequest(BaseModel):
    start: Point2D
    goal: Point2D
    frame: str = "map"

class NavGoalRequest(Pose2D):
    frame: str = "map"
    behavior: Optional[str] = None
    tolerance_m: float = 0.25

class FollowWaypointsRequest(BaseModel):
    frame: str = "map"
    waypoints: List[Point2D] = Field(default_factory=list)
    loop: bool = False
    speed_mps: Optional[float] = None

class RecoveryRequest(BaseModel):
    issue: str = "unknown"
    context: Dict[str, Any] = Field(default_factory=dict)

class ActivePlan(BaseModel):
    plan_id: str
    frame: str
    status: str
    waypoints: List[Point2D] = Field(default_factory=list)
    route_points: List[Point2D] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
