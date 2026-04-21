from __future__ import annotations
from typing import Any, Dict
import requests
from .config import settings


def forward_command(translated: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{settings.cerberus_api_url.rstrip('/')}/command"
    try:
        response = requests.post(url, json=translated, timeout=settings.timeout_seconds)
        return {
            "forwarded": True,
            "status_code": response.status_code,
            "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else {"text": response.text},
            "target_url": url,
        }
    except Exception as exc:
        return {
            "forwarded": False,
            "target_url": url,
            "error": str(exc),
        }
