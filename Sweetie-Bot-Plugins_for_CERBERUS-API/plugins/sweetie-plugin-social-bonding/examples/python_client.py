import requests
base = "http://localhost:7000"

print(requests.post(f"{base}/execute", json={
    "type":"bonding.register_human",
    "payload":{"human_id":"dev-001","name":"Developer","tier":"best_friend","tags":["operator","developer"]}
}).json())

print(requests.post(f"{base}/execute", json={
    "type":"bonding.observe_human",
    "payload":{"human_id":"dev-001","event":"positive_interaction","closeness_m":1.0}
}).json())
