from pydantic import BaseModel, Field
from typing import Any, Dict, List

class PublishEventRequest(BaseModel):
    topic: str
    source: str = "unknown"
    payload: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

class SubscribeRequest(BaseModel):
    subscriber_id: str
    topics: List[str] = Field(default_factory=list)

class PollRequest(BaseModel):
    subscriber_id: str
    limit: int = 10
