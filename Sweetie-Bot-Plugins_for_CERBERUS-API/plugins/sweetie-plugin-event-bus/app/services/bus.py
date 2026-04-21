from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, UTC
import uuid
from app.config import settings

def now_iso(): return datetime.now(UTC).isoformat()

def topic_matches(pattern: str, topic: str) -> bool:
    return topic.startswith(pattern[:-1]) if pattern.endswith("*") else pattern == topic

def category_for_topic(topic: str) -> str:
    if topic.startswith("vision."): return "perception"
    if topic.startswith("cognition."): return "cognition"
    if topic.startswith("bonding."): return "social"
    if topic.startswith("autonomy."): return "autonomy"
    if topic.startswith("crusader."): return "peer"
    if topic.startswith("docking."): return "docking"
    return "general"

@dataclass
class State:
    subscribers: dict = field(default_factory=dict)
    queues: dict = field(default_factory=dict)
    recent_events: deque = field(default_factory=lambda: deque(maxlen=settings.max_recent_events))
    published_count: int = 0
state = State()

def subscribe(subscriber_id: str, topics: list[str]):
    state.subscribers[subscriber_id] = topics[:]
    state.queues.setdefault(subscriber_id, deque())
    return {"subscriber_id": subscriber_id, "topics": topics}

def unsubscribe(subscriber_id: str):
    removed = subscriber_id in state.subscribers
    state.subscribers.pop(subscriber_id, None)
    state.queues.pop(subscriber_id, None)
    return {"subscriber_id": subscriber_id, "removed": removed}

def publish(topic: str, source: str, payload: dict, tags: list[str]):
    event = {"event_id": str(uuid.uuid4()), "topic": topic, "category": category_for_topic(topic), "source": source, "payload": payload, "tags": tags, "created_at": now_iso()}
    delivered = []
    for sid, patterns in state.subscribers.items():
        if any(topic_matches(p, topic) for p in patterns):
            state.queues.setdefault(sid, deque()).append(event)
            delivered.append(sid)
    state.recent_events.appendleft(event)
    state.published_count += 1
    return {"event": event, "delivered_to": delivered}

def poll(subscriber_id: str, limit: int):
    q = state.queues.get(subscriber_id)
    if q is None: return {"subscriber_id": subscriber_id, "events": [], "remaining": 0}
    out = []
    for _ in range(max(0, limit)):
        if not q: break
        out.append(q.popleft())
    return {"subscriber_id": subscriber_id, "events": out, "remaining": len(q)}

def recent(limit: int = 25): return list(list(state.recent_events)[:limit])
def clear():
    a,b = len(state.subscribers), len(state.queues)
    state.subscribers.clear(); state.queues.clear(); state.recent_events.clear(); state.published_count = 0
    return {"cleared_subscribers": a, "cleared_queues": b}

def status():
    return {"subscriber_count": len(state.subscribers), "queue_count": len(state.queues), "published_count": state.published_count, "recent_event_count": len(state.recent_events), "subscribers": state.subscribers}
