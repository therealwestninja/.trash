# Integration Pack v2 Overview

## Goal

Move Sweetie-Bot from "well-designed plugin ecosystem" to "repeatable embodied runtime loop."

## Design principles

1. Plugins remain independent
2. Hardware dependencies are isolated inside adapters
3. Controller integration is config-driven
4. Every important flow must be testable without rewriting the stack
5. Real hardware and simulated hardware should share the same contracts whenever possible

## First-class flows

### Flow A — best friend follow
- perception adapter reports best-friend target
- social bonding confirms priority
- attention locks target
- cognition and autonomy select follow mode
- safety approves
- runtime dispatches follow chain
- motion adapter translates movement into CERBERUS-compatible motion requests

### Flow B — low battery dock
- battery adapter reports low battery
- autonomy supervisor switches to dock mode
- docking behavior plans approach
- navigation produces route
- motion adapter executes movement
- charging adapter reports docked/charging

### Flow C — peer status ping
- crusader link chooses Bluetooth > Wi-Fi > voice
- runtime emits team status ping
- controller displays peer health/state

## What remains intentionally stubbed
- actual CV model binding
- actual microphone/speaker hardware drivers
- actual Bluetooth stack binding
- actual Unitree motor command binding through CERBERUS

Those are isolated so they can be replaced independently.
