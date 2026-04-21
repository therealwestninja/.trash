# Implementation Roadmap

## Phase 1: Contract Stabilization
- Add the shared SDK
- Add request and response schemas
- Add manifest schema
- Add event and command schemas
- Add a reference plugin template
- Validate manifests in CI

## Phase 2: Controller Foundation
- Build the controller skeleton
- Add plugin registry loading
- Add state store
- Add trace logger
- Add patch ownership validation
- Add event fanout hooks

## Phase 3: Core Cognition
- Mission Executive
- Mood
- Social
- Attention Manager
- Behavior Engine
- Expressive Behavior

## Phase 4: Safe Action Path
- Action Registry
- Safety Layer
- Runtime Adapter
- Motion and audio adapters

## Phase 5: Character Continuity
- World Model
- Memory
- Dialogue Style
- Voice Intent
- Learning Loop integration

## Suggested Order of Real Work
1. shared SDK
2. schemas
3. controller
4. mission executive
5. mood
6. social
7. behavior engine
8. expressive behavior
9. safety layer
10. runtime adapter

## Success Criteria
The architecture is ready when:
- Plugins share one execute contract
- Controller enforces ownership and logging
- Safety sits between cognition and actuation
- Core character systems can be swapped without breaking orchestration
