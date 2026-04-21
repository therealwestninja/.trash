from __future__ import annotations


def make_event(event_type: str, data: dict | None = None) -> dict:
    return {
        "type": event_type,
        "data": data or {},
    }
