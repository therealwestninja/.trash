from dataclasses import dataclass, field
from datetime import datetime, UTC
from app.models import ActionRegistration

def now_iso(): return datetime.now(UTC).isoformat()

DEFAULT_ACTIONS = [
    {
        "action_name":"follow_operator",
        "description":"Follow the best-friend/operator target.",
        "handler_type":"plugin_execute",
        "target_plugin":"runtime-orchestrator",
        "target_action":"runtime.follow_best_friend",
        "default_payload":{},
        "tags":["follow","operator","social"],
        "policy":{"safety_level":"normal","relationship_required":"best_friend"}
    },
    {
        "action_name":"idle_scan",
        "description":"Low-risk idle scan behavior.",
        "handler_type":"plugin_execute",
        "target_plugin":"runtime-orchestrator",
        "target_action":"runtime.chain_execute",
        "default_payload":{"chain_name":"peer_status_ping","payload":{}},
        "tags":["idle","observe"],
        "policy":{"safety_level":"low"}
    },
    {
        "action_name":"seek_dock",
        "description":"Enter docking cycle.",
        "handler_type":"plugin_execute",
        "target_plugin":"runtime-orchestrator",
        "target_action":"runtime.dock_cycle",
        "default_payload":{},
        "tags":["dock","battery","autonomy"],
        "policy":{"safety_level":"strict"}
    },
    {
        "action_name":"peer_status_ping",
        "description":"Send status message to a Crusader peer.",
        "handler_type":"plugin_execute",
        "target_plugin":"runtime-orchestrator",
        "target_action":"runtime.peer_status_ping",
        "default_payload":{},
        "tags":["peer","team","communication"],
        "policy":{"safety_level":"normal"}
    }
]

@dataclass
class Entry:
    action: ActionRegistration
    created_at: str
    updated_at: str
    def dump(self): return {"action": self.action.model_dump(), "created_at": self.created_at, "updated_at": self.updated_at}

@dataclass
class State:
    actions: dict = field(default_factory=dict)
    dispatch_count: int = 0
    recent_dispatches: list[dict] = field(default_factory=list)
state = State()

def register_action(model: ActionRegistration):
    ts = now_iso()
    existing = state.actions.get(model.action_name)
    created_at = existing.created_at if existing else ts
    entry = Entry(action=model, created_at=created_at, updated_at=ts)
    state.actions[model.action_name] = entry
    return entry.dump()

def unregister_action(name: str):
    removed = state.actions.pop(name, None)
    return {"action_name": name, "removed": bool(removed)}

def list_actions():
    return [e.dump() for _,e in sorted(state.actions.items(), key=lambda kv: kv[0])]

def get_action(name: str):
    e = state.actions.get(name)
    return e.dump() if e else None

def set_policy(name: str, policy: dict):
    e = state.actions.get(name)
    if not e: return None
    data = e.action.model_dump(); data["policy"] = policy
    state.actions[name] = Entry(ActionRegistration(**data), e.created_at, now_iso())
    return state.actions[name].dump()

def dispatch(name: str, payload_override: dict):
    e = state.actions.get(name)
    if not e: return None
    merged = {**e.action.default_payload, **payload_override}
    env = {
        "dispatch_type": e.action.handler_type,
        "target_plugin": e.action.target_plugin,
        "execute_request": {"type": e.action.target_action, "payload": merged},
        "policy": e.action.policy,
        "tags": e.action.tags,
    }
    state.dispatch_count += 1
    state.recent_dispatches.append({"action_name": name, "target_plugin": e.action.target_plugin, "target_action": e.action.target_action, "dispatched_at": now_iso()})
    state.recent_dispatches = state.recent_dispatches[-20:]
    return {"action_name": name, "dispatch_envelope": env, "description": e.action.description}

def seed_defaults():
    seeded = []
    for item in DEFAULT_ACTIONS:
        seeded.append(register_action(ActionRegistration(**item)))
    return {"seeded_count": len(seeded), "results": seeded}

def status():
    return {"action_count": len(state.actions), "dispatch_count": state.dispatch_count, "recent_dispatches": state.recent_dispatches[-10:]}
