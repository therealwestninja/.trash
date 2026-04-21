# Sweetie-Bot Plugin Ecosystem

🤖 Sweetie-Bot is a modular plugin ecosystem designed to extend and enhance the CERBERUS API and Unitree GO2 robotics platform.

**Backend** https://github.com/therealwestninja/CERBERUS-UnitreeGo2CompanionAPI  
**Interface:** https://github.com/therealwestninja/CERBERUS-UnitreeGo2Companion_Web-Interface  
**Plugins: (You are here →)** https://github.com/therealwestninja/Sweetie-Bot-Plugins_for_CERBERUS-API

## Vision
A fully autonomous AI character capable of:
- Understanding its environment
- Interacting with humans socially
- Learning over time
- Acting safely and independently

## Architecture
Sweetie-Bot is composed of isolated containerized plugins communicating via:
- REST `/execute` endpoints
- Event Bus
- Action Registry

## Key Systems
- Perception
- Memory (Alaya + Consolidator)
- Social Bonding
- Attention + Cognition
- Behavior Engine
- Autonomy Supervisor
- Safety Governor
- Runtime Orchestrator

## Plugins (Current)
- Event Bus
- Action Registry
- Gait Library
- Social Bonding
- Crusader Link
- Autonomy Supervisor
- (and many more evolving modules)

## How Plugins Work
Each plugin:
- Runs independently
- Exposes `/execute`, `/health`, `/manifest`
- Can be replaced without breaking the system

## Controller Integration
The CERBERUS Controller communicates with plugins via:
- HTTP calls
- Config-driven endpoints

## Future Direction
- Full autonomy
- Human identity recognition
- Peer robot coordination
- Real-world deployment safety

## How to Build Plugins
1. Create a folder
2. Add `plugin.yaml`
3. Implement `/execute`
4. Containerize (Docker)
5. Register in Controller config
