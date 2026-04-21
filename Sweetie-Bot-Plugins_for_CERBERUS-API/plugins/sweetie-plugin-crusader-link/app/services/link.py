from dataclasses import dataclass, field
from datetime import datetime, UTC

PRIORITY = ["bluetooth","wifi","voice"]

def now_iso(): return datetime.now(UTC).isoformat()

@dataclass
class PeerState:
    peer_id: str
    name: str
    role: str
    transports: dict
    battery: float | None = None
    status: str = "unknown"
    last_seen: str | None = None
    def dump(self): return self.__dict__.copy()

@dataclass
class State:
    peers: dict = field(default_factory=dict)
    history: list[dict] = field(default_factory=list)
state = State()

def remember(entry):
    state.history.append({"at": now_iso(), **entry}); state.history = state.history[-50:]

def choose_transport_for(transports):
    for key in PRIORITY:
        if transports.get(key): return key
    return None

def register_peer(peer_id, name, role, transports):
    if peer_id not in state.peers and len(state.peers) >= 2:
        raise ValueError("max_peers_reached")
    p = state.peers.get(peer_id) or PeerState(peer_id, name, role, {})
    p.name = name; p.role = role; p.transports = {**p.transports, **transports}; p.last_seen = now_iso()
    state.peers[peer_id] = p
    remember({"event":"register_peer","peer_id":peer_id})
    return p.dump()

def update_link(peer_id, transports, battery, status):
    p = state.peers[peer_id]
    p.transports = {**p.transports, **transports}
    if battery is not None: p.battery = float(battery)
    if status is not None: p.status = status
    p.last_seen = now_iso()
    remember({"event":"update_link","peer_id":peer_id})
    return p.dump()

def send_message(peer_id, message_type, payload):
    p = state.peers[peer_id]
    transport = choose_transport_for(p.transports)
    env = {
        "peer_id": peer_id,
        "peer_name": p.name,
        "peer_role": p.role,
        "message_type": message_type,
        "payload": payload,
        "chosen_transport": transport,
        "fallback_order": PRIORITY,
        "team_context": {"peer_count": len(state.peers)},
    }
    remember({"event":"send_message","peer_id":peer_id,"message_type":message_type,"transport":transport})
    return env

def list_peers(): return [p.dump() for p in state.peers.values()]
def get_state(): return {"peer_count": len(state.peers), "peers": list_peers(), "history": state.history[-10:]}
def reset():
    state.peers.clear(); state.history.clear()
    return get_state()
