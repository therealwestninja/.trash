from typing import Dict, Any
import httpx

async def call_execute(url: str, payload: Dict[str, Any]) -> Dict[str, Any] | None:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(f"{url.rstrip('/')}/execute", json=payload)
            r.raise_for_status()
            return r.json()
    except Exception:
        return None
