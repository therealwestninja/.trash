from __future__ import annotations

from typing import Any, Dict
import httpx

from app.config import settings

async def maybe_forward(action_type: str, payload: Dict[str, Any]) -> Dict[str, Any] | None:
    if not settings.forward_to_ros2:
        return None

    target_payload = {
        "type": "ros2.action_goal",
        "payload": {
            "action_name": action_type,
            "goal": payload,
        },
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(f"{settings.ros2_bridge_url}/execute", json=target_payload)
        response.raise_for_status()
        return response.json()
