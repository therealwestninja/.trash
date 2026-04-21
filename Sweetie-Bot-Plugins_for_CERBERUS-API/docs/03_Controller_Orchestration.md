# Controller Orchestration Design

## Role of the Controller
The controller is the orchestrator for the plugin ecosystem.
It should be responsible for transport, ordering, state merge, tracing, and safety enforcement.
It should not become the home for plugin domain logic.

## Recommended Tick Flow
1. Receive user input, perception event, or scheduled trigger.
2. Normalize it into the standard input envelope.
3. Load current session state.
4. Call plugins in a deterministic order.
5. Merge returned state patches.
6. Fan out emitted events.
7. Resolve action intents.
8. Run safety validation.
9. Dispatch through runtime adapter.
10. Save updated state and trace.

## Recommended Order
1. Attention Manager
2. Social
3. Mood
4. Mission Executive
5. Behavior Engine
6. Expressive Behavior
7. Action Registry
8. Safety Layer
9. Runtime Adapter

## Why this order works
Attention decides what matters.
Social decides who matters.
Mood colors response selection.
Mission decides what the system is trying to accomplish.
Behavior selects what to do next.
Expression determines how to do it in-character.
Action, safety, and runtime convert that into execution.

## Pseudocode
```python
state = store.load(session_id)

attention = call_plugin("attention.select_focus", state, event)
state = merge(state, attention.state_patch)

social = call_plugin("social.rank_targets", state, event)
state = merge(state, social.state_patch)

mood = call_plugin("mood.update", state, event)
state = merge(state, mood.state_patch)

mission = call_plugin("mission.plan", state, event)
state = merge(state, mission.state_patch)

behavior = call_plugin("behavior.select", state, event)
state = merge(state, behavior.state_patch)

expression = call_plugin("expression.compose", state, event)
state = merge(state, expression.state_patch)

command = resolve_command(behavior, expression)
validated = call_plugin("safety.validate_command", state, command)

if validated.ok:
    runtime = call_plugin("runtime.execute", state, command)
    state = merge(state, runtime.state_patch)

store.save(session_id, state)
```

## Controller Responsibilities
- plugin discovery
- manifest validation
- endpoint registry
- request timeout handling
- retry policy where appropriate
- state merge and ownership checks
- event bus publication
- trace logs
- metrics
- manual override paths

## Controller Anti-Patterns
Avoid putting these directly in the controller:
- emotional state logic
- relationship scoring
- goal planning
- expression composition
- hardware-specific routines

## Safety Note
No cognition plugin should directly issue raw motor or actuator instructions. The safety layer and runtime adapter must remain between decision-making and hardware execution.
