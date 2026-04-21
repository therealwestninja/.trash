from dataclasses import dataclass, field
from datetime import datetime, UTC
from app.config import settings

PROVIDERS = [
    {"provider":"mock","kind":"local_stub","notes":"Transcript-first development mode"},
    {"provider":"whisper_local","kind":"local","notes":"Planned local STT backend"},
    {"provider":"cloud_openai_compatible","kind":"remote","notes":"Planned remote STT backend"},
]

@dataclass
class State:
    provider: str = settings.default_provider
    language: str = settings.default_language
    mode: str = settings.default_mode
    recent_requests: list[dict] = field(default_factory=list)
state = State()

def now_iso(): return datetime.now(UTC).isoformat()

def set_defaults(data):
    if data.get("provider"): state.provider = data["provider"]
    if data.get("language"): state.language = data["language"]
    if data.get("mode"): state.mode = data["mode"]
    return get_defaults()

def get_defaults():
    return {"provider": state.provider, "language": state.language, "mode": state.mode}

def list_providers(): return PROVIDERS

def transcribe(transcript, audio_reference, provider, language, metadata):
    if transcript:
        text = transcript.strip(); source_kind = "direct_transcript"
    elif audio_reference:
        text = f"[mock transcript from {audio_reference}]"; source_kind = "mock_audio_reference"
    else:
        text = ""; source_kind = "empty"
    res = {"provider": provider or state.provider, "language": language or state.language, "source_kind": source_kind, "transcript": text, "metadata": metadata}
    state.recent_requests.append({"at": now_iso(), "type":"transcribe", **res}); state.recent_requests = state.recent_requests[-20:]
    return res

def classify_utterance(text: str):
    n = text.lower().strip()
    patterns = [
        (["follow me","come with me"], "follow_operator", {"target":"speaker"}, 0.92),
        (["stop","freeze","stay there"], "stop_motion", {}, 0.93),
        (["come here","come to me"], "approach_speaker", {"target":"speaker"}, 0.90),
        (["go dock","go to the dock","go charge","time to charge"], "seek_dock", {}, 0.92),
        (["look at me","watch me"], "observe_person", {"target":"speaker"}, 0.84),
        (["check the others","ping the crusaders","status check"], "peer_status_ping", {}, 0.83),
        (["regroup","stay together"], "peer_regroup", {}, 0.80),
    ]
    for phrases, cmd, entities, conf in patterns:
        if any(p in n for p in phrases):
            return {"intent_type":"command","command_name":cmd,"confidence":conf,"entities":entities}
    if n.endswith("?") or n.startswith(("what","why","how","who","where","can you")):
        return {"intent_type":"question","command_name":None,"confidence":0.72,"entities":{}}
    if any(w in n for w in ["hi","hello","hey sweetie","good girl"]):
        return {"intent_type":"social","command_name":"greet_back","confidence":0.80,"entities":{}}
    return {"intent_type":"chat","command_name":None,"confidence":0.56,"entities":{}}

def process_utterance(transcript, speaker_id, provider, language, metadata):
    transcribed = transcribe(transcript, None, provider, language, metadata)
    classification = classify_utterance(transcribed["transcript"])
    result = {**transcribed, "speaker_id": speaker_id, **classification}
    state.recent_requests.append({"at": now_iso(), "type":"process_utterance", **result}); state.recent_requests = state.recent_requests[-20:]
    return result

def status():
    return {**get_defaults(), "providers": list_providers(), "recent_requests": state.recent_requests[-10:]}
