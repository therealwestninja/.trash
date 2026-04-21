from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class TranscribeRequest(BaseModel):
    transcript: Optional[str] = None
    audio_reference: Optional[str] = None
    provider: Optional[str] = None
    language: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProcessUtteranceRequest(BaseModel):
    transcript: str
    speaker_id: Optional[str] = None
    provider: Optional[str] = None
    language: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SetDefaultsRequest(BaseModel):
    provider: Optional[str] = None
    language: Optional[str] = None
    mode: Optional[str] = None
