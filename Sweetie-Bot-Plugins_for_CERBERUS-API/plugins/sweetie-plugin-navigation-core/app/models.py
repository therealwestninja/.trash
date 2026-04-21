from pydantic import BaseModel, Field
from typing import Dict, List

class Point(BaseModel):
    x: float
    y: float

class SetPositionRequest(BaseModel):
    position: Point

class PlanToPointRequest(BaseModel):
    goal: Point
    purpose: str = "general"

class PlanToLocationRequest(BaseModel):
    name: str
    locations: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    purpose: str = "general"

class FollowRouteRequest(BaseModel):
    route_id: str
