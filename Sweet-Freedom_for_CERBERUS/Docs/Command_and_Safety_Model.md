# Command and Safety Model

## Why this document exists

The most important difference between a robotics demo and a robotics platform is command discipline.

The source-of-truth benchmarking report highlights the most transferable patterns from mature robotics systems as:
- goal/feedback/result actions
- explicit ownership and keepalive
- latching safety stops
- command arbitration
- simulation/real interface parity
- observability and replay fileciteturn46file0L1-L1

This document turns that into a practical target for Sweet Freedom.

---

## 1. Command philosophy

Commands should be:
- explicit
- observable
- cancellable when appropriate
- attributable to a source
- filtered through safety before reaching adapters

The system should avoid hidden behavior jumps from text input directly to hardware actions.

---

## 2. Proposed action lifecycle

A future-safe action model should support:

- created
- accepted
- running
- feedbacking
- completed
- failed
- canceled
- blocked

This is strongly inspired by ROS2 action semantics, which formalize long-running work as goal, feedback, and result. fileciteturn46file0L1-L1

---

## 3. Ownership and command source

Sweet Freedom should assume that not every action source is equal.

Examples of sources:
- operator console
- quick action buttons
- autonomous behavior
- plugin-generated command
- safety/watchdog override

The system should know:
- which source requested a command
- whether that source currently owns control
- whether a higher-priority source should override it

This is the practical version of lease/ownership and muxing patterns seen in mature systems. fileciteturn46file0L1-L1

---

## 4. Safety states

At minimum, the safety model should include:

- disarmed
- armed
- estop_latched
- degraded
- faulted

Movement-capable actions should require:
- armed state
- no E-Stop latch
- no active blocking fault
- a valid ownership / session state when that system is enabled

---

## 5. E-Stop semantics

The E-Stop should be:
- visible
- latching
- hard to clear accidentally
- logged
- broadcast to UI and diagnostics

Clearing E-Stop should be a deliberate state transition, not just a button that hides danger.

---

## 6. Comms-loss and keepalive

Loss of controller contact should not be treated as a normal idle event.

Target behavior:
- detect stale operator session / keepalive
- emit a safety event
- downgrade or stop active motion-capable behavior
- reflect the degraded state in runtime and UI

This is directly aligned with the keepalive and comms-loss policy patterns benchmarked from more mature platforms. fileciteturn46file0L1-L1

---

## 7. Arbitration

When multiple sources want control, the system should not improvise.

It should apply:
- source priority
- lock rules
- safety overrides
- deterministic winner selection

Safety and watchdog paths should always outrank convenience sources.

---

## 8. Observability

Every important safety or command transition should be easy to inspect later.

That includes:
- who requested the action
- what safety decision was made
- whether it was blocked, modified, or executed
- what happened afterward

This is essential for both testing and trust.
