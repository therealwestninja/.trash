from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
from typing import Dict, List

from app.config import settings
from app.models import PayloadDescriptor

@dataclass
class RegisteredPayload:
    descriptor: PayloadDescriptor
    registered_at: datetime
    updated_at: datetime
    expires_at: datetime | None

class PayloadRegistry:
    def __init__(self):
        self.payloads: Dict[str, RegisteredPayload] = {}

    def _now(self) -> datetime:
        return datetime.now(UTC)

    def _purge_expired(self) -> None:
        now = self._now()
        expired = [pid for pid, entry in self.payloads.items() if entry.expires_at and entry.expires_at < now]
        for pid in expired:
            self.payloads.pop(pid, None)

    def _expiry(self, ttl_seconds: int | None):
        ttl = settings.default_heartbeat_ttl_seconds if ttl_seconds is None else ttl_seconds
        if ttl <= 0:
            return None
        return self._now() + timedelta(seconds=ttl)

    def register(self, descriptor: PayloadDescriptor) -> dict:
        self._purge_expired()
        now = self._now()
        existing = self.payloads.get(descriptor.id)
        registered_at = existing.registered_at if existing else now
        entry = RegisteredPayload(
            descriptor=descriptor,
            registered_at=registered_at,
            updated_at=now,
            expires_at=self._expiry(descriptor.heartbeat_ttl_seconds),
        )
        self.payloads[descriptor.id] = entry
        return self._serialize(entry)

    def heartbeat(self, payload_id: str) -> dict | None:
        self._purge_expired()
        entry = self.payloads.get(payload_id)
        if not entry:
            return None
        entry.updated_at = self._now()
        entry.expires_at = self._expiry(entry.descriptor.heartbeat_ttl_seconds)
        return self._serialize(entry)

    def unregister(self, payload_id: str) -> bool:
        self._purge_expired()
        return self.payloads.pop(payload_id, None) is not None

    def get(self, payload_id: str) -> dict | None:
        self._purge_expired()
        entry = self.payloads.get(payload_id)
        return self._serialize(entry) if entry else None

    def list(self) -> List[dict]:
        self._purge_expired()
        return [self._serialize(entry) for entry in self.payloads.values()]

    def list_by_capability(self, capability: str) -> List[dict]:
        self._purge_expired()
        return [
            self._serialize(entry)
            for entry in self.payloads.values()
            if capability in entry.descriptor.capabilities
        ]

    def route(self, capability: str, preferred_payload_id: str | None = None) -> dict | None:
        self._purge_expired()
        if preferred_payload_id:
            entry = self.payloads.get(preferred_payload_id)
            if entry and capability in entry.descriptor.capabilities:
                return self._serialize(entry)
        matches = self.list_by_capability(capability)
        return matches[0] if matches else None

    def status(self) -> dict:
        self._purge_expired()
        capability_counts = {}
        kind_counts = {}
        for entry in self.payloads.values():
            kind_counts[entry.descriptor.kind] = kind_counts.get(entry.descriptor.kind, 0) + 1
            for cap in entry.descriptor.capabilities:
                capability_counts[cap] = capability_counts.get(cap, 0) + 1
        return {
            "payload_count": len(self.payloads),
            "kind_counts": kind_counts,
            "capability_counts": capability_counts,
        }

    def _serialize(self, entry: RegisteredPayload | None) -> dict | None:
        if not entry:
            return None
        return {
            "payload": entry.descriptor.model_dump(),
            "registered_at": entry.registered_at.isoformat(),
            "updated_at": entry.updated_at.isoformat(),
            "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
        }

registry = PayloadRegistry()
