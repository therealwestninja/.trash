# Controller Team Instructions

## Role
The Controller Team is responsible for the web/server application that directly interfaces with the Unitree GO2 robot via the CERBERUS API.

## Primary Responsibilities
- Execute motion commands safely
- Interface with hardware (GO2, sensors, battery, docking)
- Provide real-time state to Sweetie-Bot ecosystem
- Expose endpoints for plugin system

## Required Features

### Plugin Integration Layer
- Config-driven plugin endpoints
- HTTP routing to /execute
- Health monitoring for all plugins

### Real-Time State Streaming
- Battery level
- Motion state
- Position/odometry
- Docking/charging state
- Safety flags

### Control Surface
- Manual override (STOP, DOCK, FOLLOW)
- Mode switching (autonomy/manual)
- Emergency stop

### UI Panels
- Autonomy Mode + Goal
- Character State (mood, focus)
- Social Bonding
- Peer/Squad State
- Motion + Gait
- Audio I/O
- Safety Status

### Hardware Adapters
- Motion → CERBERUS API
- Battery telemetry
- Audio I/O
- Perception input
- Peer transport

## Rules
- No AI logic here
- Deterministic + safe execution only
- Controller = execution + visibility layer

## Next Tasks
1. Real motion adapter
2. UI dashboards
3. Plugin health monitoring
4. Debug tools
