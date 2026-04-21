# State Model and Ownership

## Goal
Keep shared state understandable and safe to merge.

## Top-Level State Slices
- `mission`
- `mood`
- `social`
- `attention`
- `behavior`
- `expression`
- `world`
- `memory`
- `runtime`
- `safety`

## Ownership Rule
Each slice has one authoritative owner.

| State Slice | Owner Plugin |
|---|---|
| `mission` | Mission Executive |
| `mood` | Mood Plugin |
| `social` | Social Plugin |
| `attention` | Attention Manager |
| `behavior` | Behavior Engine |
| `expression` | Expressive Behavior |
| `world` | World Model |
| `memory` | Memory Plugin |
| `runtime` | Runtime Adapter or Controller |
| `safety` | Safety Layer |

## Merge Rules
1. Owner plugins may fully patch their own slice.
2. Non-owner plugins may only add hints, annotations, or proposals.
3. Every applied patch should be tagged with source plugin, timestamp, and request ID.
4. Top-level collisions should be rejected unless the writer is the owner.

## Example
The behavior engine may propose an expression hint like:

```json
{
  "behavior": {
    "current": "greet_human",
    "expression_hint": {
      "voice_tone": "warm",
      "ear_pose": "perk"
    }
  }
}
```

But the expressive behavior plugin should own the actual `expression.current` payload that gets sent downstream.

## Suggested Mood Slice
```json
{
  "current": "curious",
  "intensity": 0.58,
  "energy": 0.67,
  "affection": 0.81,
  "last_updated": "2026-03-30T22:00:00Z"
}
```

## Suggested Mission Slice
```json
{
  "current_goal": "engage_human_helpfully",
  "goal_stack": [
    "stay_safe",
    "maintain_social_presence",
    "engage_human_helpfully"
  ],
  "interruptions": [],
  "mode": "interactive"
}
```

## Suggested Runtime Slice
```json
{
  "mode": "simulation",
  "current_action": null,
  "busy": false,
  "last_dispatch": null
}
```

## Debugging Benefit
With explicit ownership, you can answer hard questions quickly:
- Which plugin changed state?
- Was the write authoritative?
- Which request caused the current behavior?
- Which patch should be rolled back?
