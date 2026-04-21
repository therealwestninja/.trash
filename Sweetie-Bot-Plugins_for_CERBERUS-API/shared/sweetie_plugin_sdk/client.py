from __future__ import annotations

from typing import Any, Dict
import requests


def execute(base_url: str, payload: Dict[str, Any], timeout: float = 3.0) -> Dict[str, Any]:
    response = requests.post(f"{base_url.rstrip('/')}/execute", json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()
