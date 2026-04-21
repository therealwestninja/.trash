from pydantic import BaseModel, Field
from typing import Dict, Any

class RegisterPeerRequest(BaseModel):
    peer_id: str
    name: str
    role: str = "peer"
    transports: Dict[str, bool] = Field(default_factory=dict)

class UpdateLinkRequest(BaseModel):
    peer_id: str
    transports: Dict[str, bool] = Field(default_factory=dict)
    battery: float | None = None
    status: str | None = None

class SendMessageRequest(BaseModel):
    peer_id: str
    message_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)

class PeerIdRequest(BaseModel):
    peer_id: str
