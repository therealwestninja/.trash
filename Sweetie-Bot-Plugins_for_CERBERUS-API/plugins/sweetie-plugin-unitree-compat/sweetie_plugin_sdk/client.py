from __future__ import annotations
from typing import Any, Dict
import requests

class SweetiePluginClient:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def health(self) -> Dict[str, Any]:
        return requests.get(f"{self.base_url}/health", timeout=self.timeout).json()

    def manifest(self) -> Dict[str, Any]:
        return requests.get(f"{self.base_url}/manifest", timeout=self.timeout).json()

    def execute(self, action_type: str, payload: Dict[str, Any] | None = None, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        body = {"type": action_type, "payload": payload or {}, "context": context or {}}
        return requests.post(f"{self.base_url}/execute", json=body, timeout=self.timeout).json()
