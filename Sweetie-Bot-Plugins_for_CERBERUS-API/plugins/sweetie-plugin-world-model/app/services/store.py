from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
from math import sqrt
from typing import Dict, List

from app.config import settings
from app.models import QueryNearRequest, WorldObject

@dataclass
class StoredWorldObject:
    obj: WorldObject
    updated_at: datetime
    expires_at: datetime | None

class WorldStore:
    def __init__(self):
        self.objects: Dict[str, StoredWorldObject] = {}

    def _now(self) -> datetime:
        return datetime.now(UTC)

    def _purge_expired(self) -> None:
        now = self._now()
        expired = [obj_id for obj_id, entry in self.objects.items() if entry.expires_at and entry.expires_at < now]
        for obj_id in expired:
            self.objects.pop(obj_id, None)

    def _expires_for(self, ttl_seconds: int | None):
        if ttl_seconds is None:
            ttl_seconds = settings.default_ttl_seconds
        if ttl_seconds <= 0:
            return None
        return self._now() + timedelta(seconds=ttl_seconds)

    def upsert(self, obj: WorldObject) -> dict:
        self._purge_expired()
        entry = StoredWorldObject(
            obj=obj,
            updated_at=self._now(),
            expires_at=self._expires_for(obj.ttl_seconds),
        )
        self.objects[obj.id] = entry
        return self._serialize_entry(entry)

    def get(self, obj_id: str) -> dict | None:
        self._purge_expired()
        entry = self.objects.get(obj_id)
        return self._serialize_entry(entry) if entry else None

    def list(self) -> List[dict]:
        self._purge_expired()
        return [self._serialize_entry(entry) for entry in self.objects.values()]

    def delete(self, obj_id: str) -> bool:
        self._purge_expired()
        return self.objects.pop(obj_id, None) is not None

    def clear(self) -> int:
        count = len(self.objects)
        self.objects.clear()
        return count

    def query_near(self, query: QueryNearRequest) -> List[dict]:
        self._purge_expired()
        labels = set(query.labels)
        categories = set(query.categories)
        out: List[dict] = []
        for entry in self.objects.values():
            obj = entry.obj
            if labels and obj.label not in labels:
                continue
            if categories and obj.category not in categories:
                continue
            d = sqrt(
                (obj.position.x - query.origin.x) ** 2
                + (obj.position.y - query.origin.y) ** 2
                + (obj.position.z - query.origin.z) ** 2
            )
            if d <= query.radius_m:
                serialized = self._serialize_entry(entry)
                serialized["distance_m"] = round(d, 4)
                out.append(serialized)
        out.sort(key=lambda x: x.get("distance_m", 999999))
        return out

    def status(self) -> dict:
        self._purge_expired()
        labels = {}
        for entry in self.objects.values():
            labels[entry.obj.label] = labels.get(entry.obj.label, 0) + 1
        return {
            "object_count": len(self.objects),
            "labels": labels,
        }

    def _serialize_entry(self, entry: StoredWorldObject | None) -> dict | None:
        if not entry:
            return None
        return {
            "object": entry.obj.model_dump(),
            "updated_at": entry.updated_at.isoformat(),
            "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
        }

store = WorldStore()
