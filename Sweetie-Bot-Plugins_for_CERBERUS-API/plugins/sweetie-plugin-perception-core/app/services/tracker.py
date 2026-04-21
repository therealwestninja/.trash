import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Dict, Any, List

def now():
    return datetime.now(UTC).isoformat()

@dataclass
class Track:
    track_id: str
    label: str
    confidence: float
    position: Dict[str, float]
    tags: List[str]
    source: str
    human_role: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_seen: str = ""

    def dump(self):
        return {
            "track_id": self.track_id,
            "label": self.label,
            "confidence": self.confidence,
            "position": self.position,
            "tags": self.tags,
            "source": self.source,
            "human_role": self.human_role,
            "metadata": self.metadata,
            "last_seen": self.last_seen,
        }

class State:
    def __init__(self):
        self.tracks: Dict[str, Track] = {}
        self.events: List[dict] = []

state = State()

def _topic_for(track: Track, created: bool):
    if track.label == "person":
        suffix = "detected" if created else "updated"
        return f"vision.person_{suffix}"
    return f"vision.{track.label}_{'detected' if created else 'updated'}"

def upsert_detection(det, source):
    track_id = det.id or f"{det.label}-{uuid.uuid4()}"
    created = track_id not in state.tracks
    track = state.tracks.get(track_id)
    if not track:
        track = Track(track_id, det.label, det.confidence, det.position, det.tags, source, det.human_role, det.metadata, now())
        state.tracks[track_id] = track
    else:
        track.confidence = det.confidence
        track.position = det.position
        track.tags = det.tags
        track.source = source
        track.human_role = det.human_role
        track.metadata = det.metadata
        track.last_seen = now()

    payload = track.dump()
    if track.label == "person":
        payload["operator_visible"] = ("operator" in track.tags) or (track.human_role == "best_friend")
        payload["relationship_tier"] = track.human_role or ("supporting" if "staff" in track.tags else "public")
    event = {
        "event_id": str(uuid.uuid4()),
        "topic": _topic_for(track, created),
        "source": source,
        "payload": payload,
        "tags": track.tags,
        "created_at": now(),
    }
    state.events.append(event)
    state.events = state.events[-300:]
    return track.dump(), event

def ingest(detections, source, scene):
    tracks, events = [], []
    for det in detections:
        t, e = upsert_detection(det, source)
        tracks.append(t)
        events.append(e)
    if scene:
        events.append({
            "event_id": str(uuid.uuid4()),
            "topic": "vision.scene_update",
            "source": source,
            "payload": scene,
            "tags": [],
            "created_at": now(),
        })
    return tracks, events

def list_tracks():
    return [t.dump() for t in state.tracks.values()]

def get_track(track_id):
    t = state.tracks.get(track_id)
    return t.dump() if t else None

def export_attention_candidates():
    out = []
    for t in state.tracks.values():
        out.append({
            "target_id": t.track_id,
            "label": t.label,
            "confidence": t.confidence,
            "tags": t.tags,
            "distance_m": t.metadata.get("distance_m", 1.0),
            "novelty": t.metadata.get("novelty", 0.3),
            "salience": max(0.4, t.confidence),
            "persistence": 0.2 if t.label == "person" else 0.1,
        })
    return out

def reset():
    state.tracks.clear()
    state.events.clear()
    return {"reset": True}
