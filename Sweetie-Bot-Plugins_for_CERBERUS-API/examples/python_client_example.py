import requests

# Character plugin
reply = requests.post(
    'http://localhost:7011/execute',
    json={
        'type': 'character.reply',
        'payload': {
            'input': 'Hello Sweetie!',
            'state': {'mood': 'happy'}
        }
    },
    timeout=10,
)
print(reply.json())

# Memory plugin
memory = requests.post(
    'http://localhost:7012/memory/store',
    json={
        'session_id': 'demo',
        'namespace': 'notes',
        'key': 'favorite_gait',
        'value': 'trot'
    },
    timeout=10,
)
print(memory.json())
