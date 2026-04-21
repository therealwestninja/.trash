from dataclasses import dataclass, field
from datetime import datetime, UTC
from app.config import settings

VOICE_LIBRARY = {
    "sweetie_bright":{"label":"Sweetie Bright","base_rate":1.08,"base_pitch":1.12,"style_tags":["youthful","playful","wholesome"]},
    "sweetie_soft":{"label":"Sweetie Soft","base_rate":0.98,"base_pitch":1.05,"style_tags":["gentle","kind","soft"]},
    "sweetie_excited":{"label":"Sweetie Excited","base_rate":1.16,"base_pitch":1.18,"style_tags":["enthusiastic","bubbly","expressive"]},
    "sweetie_team":{"label":"Sweetie Team","base_rate":1.05,"base_pitch":1.10,"style_tags":["cooperative","clear","friendly"]},
}

@dataclass
class State:
    provider: str = settings.default_provider
    voice: str = settings.default_voice
    rate: float = settings.default_rate
    pitch: float = settings.default_pitch
    recent_requests: list[dict] = field(default_factory=list)
state = State()

def now_iso(): return datetime.now(UTC).isoformat()
def clamp(v,lo,hi): return max(lo,min(hi,float(v)))

def list_voices():
    return [{"voice":k, **v} for k,v in VOICE_LIBRARY.items()]

def set_defaults(data):
    if data.get("provider"): state.provider = data["provider"]
    if data.get("voice"): state.voice = data["voice"]
    if data.get("rate") is not None: state.rate = clamp(data["rate"],0.5,2.0)
    if data.get("pitch") is not None: state.pitch = clamp(data["pitch"],0.5,2.0)
    return get_defaults()

def get_defaults():
    return {"provider": state.provider, "voice": state.voice, "rate": state.rate, "pitch": state.pitch}

def build_speech(text, tone, emotion, voice, provider, rate, pitch, metadata):
    voice_name = voice or ("sweetie_team" if metadata.get("peer_context") else state.voice)
    voice_meta = VOICE_LIBRARY.get(voice_name, VOICE_LIBRARY["sweetie_bright"])
    base_rate = rate if rate is not None else voice_meta["base_rate"] * state.rate
    base_pitch = pitch if pitch is not None else voice_meta["base_pitch"] * state.pitch
    tags = list(voice_meta["style_tags"])

    rel = metadata.get("relationship_tier")
    mode = metadata.get("autonomy_mode")
    if rel == "best_friend":
        base_pitch *= 1.03; tags += ["warm","attached"]
    elif rel == "public":
        base_rate *= 0.97; tags += ["polite","careful"]

    if mode in {"dock_seek","dock_urgent","charging"}:
        base_rate *= 0.94; tags += ["calm","practical"]
    elif mode == "follow_operator":
        base_rate *= 1.03; base_pitch *= 1.02; tags += ["eager"]

    if tone == "bright_cheerful":
        base_rate *= 1.03; base_pitch *= 1.03
    elif tone == "soft_careful":
        base_rate *= 0.95; base_pitch *= 0.98
    elif tone == "dramatic_cute":
        base_pitch *= 1.05

    if emotion == "excited":
        base_rate *= 1.05; base_pitch *= 1.04
    elif emotion == "tired":
        base_rate *= 0.92; base_pitch *= 0.97

    env = {
        "provider": provider or state.provider,
        "voice": voice_name,
        "text": text,
        "rate": round(clamp(base_rate,0.5,2.0),4),
        "pitch": round(clamp(base_pitch,0.5,2.0),4),
        "tone": tone,
        "emotion": emotion,
        "style_tags": list(dict.fromkeys(tags)),
        "metadata": metadata,
        "synthesis_request":{"provider": provider or state.provider,"voice": voice_name,"text": text}
    }
    state.recent_requests.append({"at": now_iso(), **env})
    state.recent_requests = state.recent_requests[-20:]
    return env

def preview_voice(voice, sample_text):
    return build_speech(sample_text, "warm_playful", "neutral", voice, None, None, None, {"preview": True})

def status():
    return {**get_defaults(), "voices": list_voices(), "recent_requests": state.recent_requests[-10:]}
