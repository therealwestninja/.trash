from dataclasses import dataclass
from typing import Dict, Any

GAITS = {
    "canine":{
        "walk":{"cadence_hint_hz":1.4,"duty_factor":0.72,"bounce":"low","body_carriage":"neutral","speed_range_mps":[0.2,0.9]},
        "trot":{"cadence_hint_hz":2.2,"duty_factor":0.55,"bounce":"medium","body_carriage":"forward","speed_range_mps":[0.8,1.8]},
        "canter":{"cadence_hint_hz":2.8,"duty_factor":0.42,"bounce":"medium_high","body_carriage":"forward","speed_range_mps":[1.4,2.6]},
        "gallop":{"cadence_hint_hz":3.5,"duty_factor":0.32,"bounce":"high","body_carriage":"aggressive_forward","speed_range_mps":[2.2,4.5]},
    },
    "equine":{
        "walk":{"cadence_hint_hz":1.3,"duty_factor":0.74,"bounce":"low","body_carriage":"head_nod","speed_range_mps":[0.2,0.8]},
        "trot":{"cadence_hint_hz":2.0,"duty_factor":0.52,"bounce":"high","body_carriage":"collected_or_forward","speed_range_mps":[0.8,1.8]},
        "canter":{"cadence_hint_hz":2.5,"duty_factor":0.43,"bounce":"rolling","body_carriage":"lead_based","speed_range_mps":[1.5,2.8]},
        "tolt":{"cadence_hint_hz":2.0,"duty_factor":0.66,"bounce":"very_low","body_carriage":"smooth_upright","speed_range_mps":[0.8,2.5]},
    }
}

@dataclass
class State:
    active_profile: str = "canine"
    active_gait: str = "walk"
state = State()

def list_profiles(): return sorted(GAITS.keys())
def list_gaits(profile: str): return sorted(GAITS.get(profile, {}).keys())
def get_gait(profile: str, gait: str): return GAITS.get(profile, {}).get(gait)

def set_active(profile: str, gait: str):
    if profile not in GAITS or gait not in GAITS[profile]:
        raise KeyError("unknown_gait")
    state.active_profile = profile; state.active_gait = gait
    return get_active()

def get_active():
    return {"active_profile": state.active_profile, "active_gait": state.active_gait, "gait": GAITS[state.active_profile][state.active_gait]}

def adapt_command(command: dict, profile=None, gait=None, autonomy_mode=None, movement_style=None):
    prof = profile or state.active_profile
    gt = gait or state.active_gait
    meta = get_gait(prof, gt)
    if not meta: raise KeyError("unknown_gait")
    payload = dict(command.get("payload", {}))
    speed = float(payload.get("speed_mps", meta["speed_range_mps"][0]))

    if autonomy_mode in {"dock_seek","dock_urgent","charging"}:
        speed = min(speed or meta["speed_range_mps"][0], 0.6)
        payload["movement_bias"] = "careful"
    elif movement_style in {"light_trot","loyal_follow"}:
        speed = max(speed, 0.9)
        payload["movement_bias"] = "social"
    elif movement_style in {"curious_prance","curious_investigate"}:
        payload["movement_bias"] = "playful"

    adapted = {
        "type": command.get("type","robot.command"),
        "payload": {
            **payload,
            "movement_profile": prof,
            "movement_gait": gt,
            "gait_meta": meta,
            "recommended_speed_mps": max(meta["speed_range_mps"][0], min(speed, meta["speed_range_mps"][1])),
            "autonomy_mode": autonomy_mode,
            "movement_style": movement_style,
        }
    }
    return {"active_profile": prof, "active_gait": gt, "gait": meta, "adapted_command": adapted}

def preview_sequence(profile=None, gait=None, seconds=3.0):
    prof = profile or state.active_profile
    gt = gait or state.active_gait
    meta = get_gait(prof, gt)
    cycles = max(1, int(round(seconds * meta["cadence_hint_hz"])))
    return {"active_profile": prof, "active_gait": gt, "seconds": seconds, "estimated_cycles": cycles, "preview":[{"cycle":i+1,"body_carriage":meta["body_carriage"],"bounce":meta["bounce"]} for i in range(cycles)]}
