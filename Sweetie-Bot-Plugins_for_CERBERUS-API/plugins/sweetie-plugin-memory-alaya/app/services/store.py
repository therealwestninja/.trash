from __future__ import annotations
import math, uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
from typing import Dict
from app.config import settings

def now():
    return datetime.now(UTC)

def tokenize(text: str) -> set[str]:
    cleaned = "".join(c.lower() if c.isalnum() else " " for c in text)
    return {t for t in cleaned.split() if t}

@dataclass
class MemoryEntry:
    id: str
    memory_type: str
    text: str
    tags: list[str]
    source: str
    salience: float
    metadata: dict
    created_at: datetime
    updated_at: datetime
    expires_at: datetime | None

    def dump(self):
        return {
            "id": self.id,
            "memory_type": self.memory_type,
            "text": self.text,
            "tags": self.tags,
            "source": self.source,
            "salience": self.salience,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

class Store:
    def __init__(self):
        self.entries: Dict[str, MemoryEntry] = {}

    def _purge(self):
        t = now()
        for k in [k for k,v in self.entries.items() if v.expires_at and v.expires_at < t]:
            self.entries.pop(k, None)

    def store(self, memory_type: str, text: str, tags: list[str], source: str, salience: float, metadata: dict, ttl_days: int | None):
        self._purge()
        t = now()
        exp = None if not ttl_days else t + timedelta(days=ttl_days)
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            memory_type=memory_type,
            text=text,
            tags=sorted(set(tags)),
            source=source,
            salience=max(0.0, min(1.0, salience)),
            metadata=metadata,
            created_at=t,
            updated_at=t,
            expires_at=exp,
        )
        self.entries[entry.id] = entry
        return entry.dump()

    def get(self, mid: str):
        self._purge()
        e = self.entries.get(mid)
        return e.dump() if e else None

    def list(self):
        self._purge()
        return [e.dump() for e in sorted(self.entries.values(), key=lambda x: x.updated_at, reverse=True)]

    def delete(self, mid: str):
        self._purge()
        return self.entries.pop(mid, None) is not None

    def _relationship_bonus(self, entry: MemoryEntry, preferred: list[str]) -> float:
        tier = (entry.metadata or {}).get("relationship_tier")
        if not tier:
            return 0.0
        if preferred and tier in preferred:
            return 0.25
        if tier == "best_friend":
            return 0.18
        if tier == "supporting":
            return 0.08
        return 0.02

    def query(self, text: str, limit: int, tags: list[str], preferred_relationship_tiers: list[str]):
        self._purge()
        q_tokens = tokenize(text)
        results = []
        for e in self.entries.values():
            e_tokens = tokenize(e.text)
            overlap = len(q_tokens & e_tokens)
            jacc = overlap / max(1, len(q_tokens | e_tokens))
            tag_overlap = len(set(tags) & set(e.tags))
            age_days = max(0.0, (now() - e.updated_at).total_seconds() / 86400.0)
            decay = math.exp(-settings.decay_per_day * age_days)
            relation_bonus = self._relationship_bonus(e, preferred_relationship_tiers)
            score = (jacc * 0.40) + (tag_overlap * 0.12) + (e.salience * 0.20) + (decay * 0.13) + relation_bonus
            if score > 0:
                item = e.dump()
                item["retrieval_score"] = round(score, 6)
                results.append(item)
        results.sort(key=lambda x: x["retrieval_score"], reverse=True)
        return results[:limit]

    def consolidate(self, min_tag_overlap: int):
        self._purge()
        created = []
        episodes = [e for e in self.entries.values() if e.memory_type == "episode"]
        seen = set()
        for i, a in enumerate(episodes):
            for b in episodes[i+1:]:
                overlap = tuple(sorted(set(a.tags) & set(b.tags)))
                if len(overlap) < min_tag_overlap or overlap in seen:
                    continue
                seen.add(overlap)
                relation = (a.metadata or {}).get("relationship_tier") or (b.metadata or {}).get("relationship_tier")
                created.append(self.store(
                    "fact",
                    f"Repeated experience suggests a stable association involving: {', '.join(overlap)}.",
                    list(overlap),
                    "memory.consolidate",
                    max(a.salience, b.salience),
                    {"derived_from":[a.id,b.id], "relationship_tier": relation},
                    365
                ))
        return created

    def status(self):
        self._purge()
        return {
            "memory_count": len(self.entries),
            "episodic_count": sum(1 for e in self.entries.values() if e.memory_type == "episode"),
            "semantic_count": sum(1 for e in self.entries.values() if e.memory_type == "fact"),
        }

store = Store()
