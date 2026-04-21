from pydantic import BaseModel, Field
from typing import Any, Dict

class ProcessEventRequest(BaseModel):
    event: Dict[str, Any] = Field(default_factory=dict)
