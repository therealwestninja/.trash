from pydantic import BaseModel
from typing import Any, Dict

class ExecuteRequest(BaseModel):
    type: str
    payload: Dict[str, Any] = {}
