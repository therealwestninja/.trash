from dataclasses import dataclass, field
from datetime import datetime, UTC

def now_iso():
    return datetime.now(UTC).isoformat()

@dataclass
class State:
    spoken: list[dict] = field(default_factory=list)
    transcripts: list[dict] = field(default_factory=list)

state = State()

def speak(payload: dict):
    entry = {"at": now_iso(), "speech_envelope": payload}
    state.spoken.append(entry)
    state.spoken = state.spoken[-30:]
    return entry

def inject_transcript(payload: dict):
    entry = {"at": now_iso(), "transcript": payload.get("transcript", "")}
    state.transcripts.append(entry)
    state.transcripts = state.transcripts[-30:]
    return entry

def get_state():
    return {"spoken": state.spoken[-10:], "transcripts": state.transcripts[-10:]}
