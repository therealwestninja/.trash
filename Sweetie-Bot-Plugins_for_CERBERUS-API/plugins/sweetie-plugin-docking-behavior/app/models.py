from pydantic import BaseModel
from typing import Optional, Dict

class Point(BaseModel):
    x: float
    y: float

class SetDockRequest(BaseModel):
    dock_name: str = "charging_dock"
    position: Point

class SeekDockRequest(BaseModel):
    battery: float
    current_position: Point

class PlanApproachRequest(BaseModel):
    current_position: Point
    dock_position: Optional[Point] = None

class AlignRequest(BaseModel):
    current_position: Point
    dock_position: Optional[Point] = None

class BeginChargeRequest(BaseModel):
    confirmed_docked: bool = False
