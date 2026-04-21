# Plugin Runtime Unification

## Problem

Sweet Freedom currently inherits two different extension models:

### CERBERUS-side model
- in-process Python plugins
- capability gating
- trust levels
- direct integration into backend runtime

### Sweetie-side model
- out-of-process HTTP services
- manifest/health/execute contract
- JSON-schema-driven requests and responses
- multi-service composition

The source-of-truth research identifies reconciling these models as a primary blocking integration task. fileciteturn44file0L1-L1

---

## Goal

The platform should expose one coherent runtime view of plugins and extensions, even if the underlying transport differs.

That means a contributor or UI module should not need to care whether something is:
- loaded in-process
- called over HTTP
- eventually bridged through another adapter model

---

## Target runtime abstraction

A useful mental model is:

`PluginRuntime = InProcessRuntime | HttpRuntime | future adapter-backed runtime`

Each runtime type should still provide a consistent surface for:
- identity
- version
- trust/capability metadata
- health
- enabled/disabled state
- available actions or capabilities
- error reporting
- event generation

---

## Why this matters

Without this unification:
- UI plugin handling stays messy
- docs drift from reality
- safety logic gets duplicated
- future capabilities become harder to reason about
- plugin ecosystems fragment instead of composing

With unification:
- plugin lists can be merged
- manifests can drive UI cards or controls
- safety policy can be applied consistently
- the backend becomes the control plane instead of a bundle of exceptions

---

## Recommended direction

### Short term
- preserve both models
- build a merged runtime registry
- normalize plugin metadata at the API layer

### Mid term
- add canonical execute pathways
- apply consistent safety and trust rules regardless of runtime type
- expose unified status and health reporting

### Long term
- support richer capability discovery
- allow UI and automation to target plugin-provided actions without runtime-specific branching

---

## Key design rule

The backend should be the place where plugin differences are reconciled.

The UI should not be forced to understand every plugin runtime style separately.
