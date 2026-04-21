import requests
base = "http://localhost:7000"

print(requests.post(f"{base}/execute", json={
    "type":"crusader.register_peer",
    "payload":{"peer_id":"cmc-applebloom","name":"Apple Bloom","role":"support","transports":{"bluetooth":True,"wifi":True,"voice":True}}
}).json())

print(requests.post(f"{base}/execute", json={
    "type":"crusader.send_message",
    "payload":{"peer_id":"cmc-applebloom","message_type":"status_ping","payload":{"battery":0.78}}
}).json())
