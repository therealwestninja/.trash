from __future__ import annotations

from time import time
from uuid import uuid4

from pydantic import BaseModel, Field


class SessionLease(BaseModel):
    lease_id: str = Field(default_factory=lambda: f"lease_{uuid4().hex[:10]}")
    owner: str = "ui"
    issued_at: float = Field(default_factory=time)
    expires_at: float = Field(default_factory=lambda: time() + 15.0)
    stale: bool = False


class KeepalivePolicy(BaseModel):
    timeout_ms: int = 15000
    on_timeout: list[str] = Field(default_factory=lambda: ["record_event", "controlled_stop", "disarm"])


class SessionLeaseManager:
    def __init__(self) -> None:
        self.lease: SessionLease | None = None
        self.policy = KeepalivePolicy()

    def acquire(self, owner: str = "ui") -> SessionLease:
        self.lease = SessionLease(owner=owner, expires_at=time() + self.policy.timeout_ms / 1000.0)
        return self.lease

    def checkin(self, lease_id: str) -> SessionLease | None:
        if not self.lease or self.lease.lease_id != lease_id:
            return None
        self.lease.expires_at = time() + self.policy.timeout_ms / 1000.0
        self.lease.stale = False
        return self.lease

    def release(self, lease_id: str) -> bool:
        if not self.lease or self.lease.lease_id != lease_id:
            return False
        self.lease = None
        return True

    def is_stale(self) -> bool:
        if not self.lease:
            return False
        if time() > self.lease.expires_at:
            self.lease.stale = True
        return self.lease.stale

    def get_state(self) -> dict:
        if not self.lease:
            return {"active": False, "lease": None, "policy": self.policy.model_dump(mode="json"), "degraded": False}
        if time() > self.lease.expires_at:
            self.lease.stale = True
        return {
            "active": True,
            "lease": self.lease.model_dump(mode="json"),
            "policy": self.policy.model_dump(mode="json"),
            "degraded": self.lease.stale,
        }
