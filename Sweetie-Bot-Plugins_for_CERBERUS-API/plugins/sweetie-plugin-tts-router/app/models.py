from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class SpeakRequest(BaseModel):
    text: str
    tone: str = "warm_playful"
    emotion: str = "neutral"
    voice: Optional[str] = None
    provider: Optional[str] = None
    rate: Optional[float] = None
    pitch: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PreviewVoiceRequest(BaseModel):
    voice: str
    sample_text: str = "Hi! I'm Sweetie!"

class SetDefaultsRequest(BaseModel):
    provider: Optional[str] = None
    voice: Optional[str] = None
    rate: Optional[float] = None
    pitch: Optional[float] = None
