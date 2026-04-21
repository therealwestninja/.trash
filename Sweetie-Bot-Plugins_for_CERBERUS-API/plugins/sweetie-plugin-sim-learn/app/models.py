from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class EpisodeStartRequest(BaseModel):
    episode_name: str
    scenario: str = "default"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class StepRequest(BaseModel):
    episode_id: str
    observation: Dict[str, Any] = Field(default_factory=dict)
    action: Dict[str, Any] = Field(default_factory=dict)
    reward: float = 0.0
    done: bool = False
    notes: List[str] = Field(default_factory=list)

class EpisodeEndRequest(BaseModel):
    episode_id: str
    outcome: str = "unknown"
    summary: Dict[str, Any] = Field(default_factory=dict)

class ReplayCreateRequest(BaseModel):
    episode_id: str

class ReplayGetRequest(BaseModel):
    replay_id: str

class DatasetExportRequest(BaseModel):
    episode_id: Optional[str] = None
