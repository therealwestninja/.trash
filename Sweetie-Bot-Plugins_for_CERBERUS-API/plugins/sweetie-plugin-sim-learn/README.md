# sweetie-plugin-sim-learn

A reusable simulation, replay, and dataset-capture plugin for the Sweetie-Bot / CERBERUS ecosystem.

This plugin gives you the **lowest-hanging-fruit learning infrastructure** without requiring full reinforcement learning or a heavy simulator on day one.

## What it does

- starts and tracks simulation or test episodes
- records timestamped steps with observations, actions, rewards, and notes
- closes episodes into reusable datasets
- creates lightweight replays that the controller or backend can inspect
- exports datasets in a stable JSON format
- gives CERBERUS a clean future upgrade path toward:
  - offline evaluation
  - imitation learning
  - controller playback
  - behavior regression testing
  - dataset collection for future AI training

## Why this matters

Without this plugin:
- experimentation is ad hoc
- behavior logs are inconsistent
- replay data is hard to reuse
- future learning pipelines have no stable input format

With this plugin:
- you can record every test as a dataset
- missions and autonomy behaviors can be replayed
- controller interactions can be captured for training data
- future policy-learning systems can build on an existing contract

## Supported execute actions

- `sim.episode_start`
- `sim.step`
- `sim.episode_end`
- `sim.replay_create`
- `sim.replay_get`
- `sim.dataset_list`
- `sim.dataset_export`
- `sim.status`

## Quick start

### Local
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7000
```

### Docker
```bash
docker build -t sweetie-plugin-sim-learn .
docker run --rm -p 7000:7000 --env-file .env.example sweetie-plugin-sim-learn
```

## Example: start an episode

```bash
curl -X POST http://localhost:7000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "type": "sim.episode_start",
    "payload": {
      "episode_name": "patrol-test-001",
      "scenario": "living-room",
      "metadata": {"operator":"dev", "mode":"simulation"}
    }
  }'
```

## Example: record a step

```json
{
  "type": "sim.step",
  "payload": {
    "episode_id": "EPISODE_ID_HERE",
    "observation": {"person_seen": true, "battery": 0.88},
    "action": {"type": "nav.goal", "payload": {"x": 2, "y": 1}},
    "reward": 0.5,
    "done": false,
    "notes": ["moving toward target"]
  }
}
```

## Example: end an episode

```json
{
  "type": "sim.episode_end",
  "payload": {
    "episode_id": "EPISODE_ID_HERE",
    "outcome": "success",
    "summary": {"distance_m": 5.2}
  }
}
```

## Example: create replay

```json
{
  "type": "sim.replay_create",
  "payload": {
    "episode_id": "EPISODE_ID_HERE"
  }
}
```

## Why it is low-hanging fruit

This plugin creates immediate practical value:
- test logging
- mission replay
- dataset capture
- safer behavior iteration
- future training compatibility

It does **not** require a full simulator or training stack to start being useful.

## Future upgrades

This plugin is intentionally a scaffold for:
- Gazebo / Isaac / Web simulation adapters
- imitation learning dataset exporters
- reward-function experiments
- regression replay tests
- future RL training jobs
