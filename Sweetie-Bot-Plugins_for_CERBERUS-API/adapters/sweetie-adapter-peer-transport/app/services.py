from dataclasses import dataclass, field

PRIORITY = ["bluetooth", "wifi", "voice"]

@dataclass
class State:
    peers: dict = field(default_factory=dict)
    outbound: list[dict] = field(default_factory=list)

state = State()

def choose_transport(transport: dict):
    for t in PRIORITY:
        if transport.get(t):
            return t
    return None

def register_peer(payload: dict):
    peer_id = payload["peer_id"]
    state.peers[peer_id] = payload.get("transport", {})
    return {"peer_id": peer_id, "transport": state.peers[peer_id], "chosen_transport": choose_transport(state.peers[peer_id])}

def send(payload: dict):
    peer_id = payload["peer_id"]
    transport = choose_transport(state.peers.get(peer_id, {}))
    env = {"peer_id": peer_id, "message_type": payload.get("message_type", "unknown"), "payload": payload.get("payload", {}), "transport": transport}
    state.outbound.append(env)
    state.outbound = state.outbound[-30:]
    return env

def get_state():
    return {"peers": state.peers, "outbound": state.outbound[-10:]}
