from __future__ import annotations

import math
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
from typing import Dict, List

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

    def dump(self) -> dict:
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

class MemoryStore:
    def __init__(self):
        self.entries: Dict[str, MemoryEntry] = {}

    def _purge_expired(self):
        t = now()
        expired = [k for k, v in self.entries.items() if v.expires_at and v.expires_at < t]
        for k in expired:
            self.entries.pop(k, None)

    def _expiry(self, memory_type: str, ttl_days: int | None):
        if ttl_days is None:
            ttl_days = settings.default_episodic_ttl_days if memory_type == "episode" else settings.default_semantic_ttl_days
        if ttl_days <= 0:
            return None
        return now() + timedelta(days=ttl_days)

    def store(self, memory_type: str, text: str, tags: list[str], source: str, salience: float, metadata: dict, ttl_days: int | None):
        self._purge_expired()
        t = now()
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
            expires_at=self._expiry(memory_type, ttl_days),
        )
        self.entries[entry.id] = entry
        return entry.dump()

    def get(self, id: str):
        self._purge_expired()
        entry = self.entries.get(id)
        return entry.dump() if entry else None

    def list(self):
        self._purge_expired()
        return [e.dump() for e in sorted(self.entries.values(), key=lambda x: x.updated_at, reverse=True)]

    def delete(self, id: str):
        self._purge_expired()
        return self.entries.pop(id, None) is not None

    def _score(self, entry: MemoryEntry, query_text: str, query_tags: list[str]) -> float:
        q_tokens = tokenize(query_text)
        e_tokens = tokenize(entry.text)
        overlap = len(q_tokens & e_tokens)
        jacc = overlap / max(1, len(q_tokens | e_tokens))
        tag_overlap = len(set(query_tags) & set(entry.tags))
        age_days = max(0.0, (now() - entry.updated_at).total_seconds() / 86400.0)
        decay = math.exp(-settings.default_decay_per_day * age_days)
        return round((jacc * 0.45) + (tag_overlap * 0.15) + (entry.salience * 0.25) + (decay * 0.15), 6)

    def query(self, query_text: str, limit: int, query_tags: list[str]):
        self._purge_expired()
        scored = []
        for entry in self.entries.values():
            score = self._score(entry, query_text, query_tags)
            if score > 0:
                scored.append((score, entry))
        scored.sort(key=lambda x: x[0], reverse=True)
        out = []
        for score, entry in scored[:limit]:
            item = entry.dump()
            item["retrieval_score"] = score
            out.append(item)
        return out

    def consolidate(self, min_tag_overlap: int = 2):
        self._purge_expired()
        episodes = [e for e in self.entries.values() if e.memory_type == "episode"]
        created = []
        seen_signatures = set()

        for i, a in enumerate(episodes):
            for b in episodes[i+1:]:
                overlap = sorted(set(a.tags) & set(b.tags))
                if len(overlap) < min_tag_overlap:
                    continue
                signature = tuple(overlap)
                if signature in seen_signatures:
                    continue
                seen_signatures.add(signature)
                summary = f"Repeated experience suggests a stable association involving: {', '.join(overlap)}."
                created.append(self.store(
                    memory_type="fact",
                    text=summary,
                    tags=overlap,
                    source="memory.consolidate",
                    salience=round((a.salience + b.salience) / 2, 4),
                    metadata={"derived_from": [a.id, b.id]},
                    ttl_days=settings.default_semantic_ttl_days,
                ))
        return created

    def status(self):
        self._purge_expired()
        episodic = sum(1 for e in self.entries.values() if e.memory_type == "episode")
        semantic = sum(1 for e in self.entries.values() if e.memory_type == "fact")
        tags = {}
        for e in self.entries.values():
            for tag in e.tags:
                tags[tag] = tags.get(tag, 0) + 1
        return {
            "memory_count": len(self.entries),
            "episodic_count": episodic,
            "semantic_count": semantic,
            "top_tags": dict(sorted(tags.items(), key=lambda kv: kv[1], reverse=True)[:10]),
        }

store = MemoryStore()
