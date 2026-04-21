from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

class ProfileRequest(BaseModel):
    profile: str

class GaitRequest(BaseModel):
    profile: str
    gait: str

class GetGaitRequest(BaseModel):
    profile: Optional[str] = None
    gait: str

class AdaptCommandRequest(BaseModel):
    profile: Optional[str] = None
    gait: Optional[str] = None
    command: Dict[str, Any] = Field(default_factory=dict)
    autonomy_mode: Optional[str] = None
    movement_style: Optional[str] = None

class PreviewSequenceRequest(BaseModel):
    profile: Optional[str] = None
    gait: Optional[str] = None
    seconds: float = 3.0
