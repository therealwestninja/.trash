# Sweetie-Bot AI Continuation Design Document

## Purpose
This document enables AI systems (ChatGPT, Claude, etc.) to continue development of Sweetie-Bot as a modular robotics AI platform.

## Core Rules
1. DO NOT create monoliths
2. EVERYTHING is a plugin
3. Plugins communicate only via APIs
4. Maintain backward compatibility

## Plugin Contract
Each plugin must expose:
- /execute
- /health
- /manifest

## Data Flow
Perception -> Event Bus -> Cognition -> Behavior -> Action Registry -> Runtime -> Robot

## Required Systems
- Perception Core
- World Model
- Identity Recognition
- Social Bonding
- Autonomy Supervisor
- Safety Layer
- Runtime Adapter

## Development Priorities
1. Real hardware integration
2. Safety systems
3. Identity recognition
4. Autonomous navigation
5. Social intelligence

## Controller Requirements
Controller must:
- Route plugin calls
- Display system state
- Allow manual overrides
- Provide debug visibility

## AI Instructions
When extending:
- Create new plugin OR extend existing plugin cleanly
- Never tightly couple plugins
- Prefer event-driven architecture
- Maintain human-safe behavior

## Long-Term Goal
A fully autonomous AI entity capable of safely existing in the real world.
