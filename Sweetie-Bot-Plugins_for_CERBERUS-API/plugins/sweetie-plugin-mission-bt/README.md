# sweetie-plugin-mission-bt

Behavior Tree mission system for CERBERUS.

## Features
- Define missions as JSON/YAML trees
- Execute sequences like patrols, routines, interactions
- Works with other plugins (nav, character, etc)

## Example Mission

```json
{
  "type": "sequence",
  "nodes": [
    {"action": "nav.goal", "payload": {"x": 2, "y": 1}},
    {"action": "wait", "payload": {"seconds": 2}},
    {"action": "nav.goal", "payload": {"x": 0, "y": 0}}
  ]
}
```

## Run
docker build -t mission-bt .
docker run -p 7000:7000 mission-bt
