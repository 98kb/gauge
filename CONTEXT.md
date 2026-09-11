# Gauge

Gauge assesses an intent and emits a planning recipe; it never executes it.

## Language

### Model profiles

**Model registry**:
The human-edited authority for model profiles and their capability bindings, separate from the planning registry.
_Avoid_: model catalog

**Model profile**:
One canonical pinned model ID plus one reasoning-effort value that model supports.
_Avoid_: execution profile, model config

**Reasoning effort**:
A model control that shapes how much the model reasons; never a measure of work size, time, or cost.
_Avoid_: effort (bare), effort estimate

**Execution boundary**:
A point in a recipe where an agent session starts: tracker setup, a planning step, the G0 implementation step, or the Implementation handoff.
_Avoid_: step (the handoff is not a step)

**Model registry gap**:
No binding exists for a boundary's capability (plus `High-assurance` when required); reported as `No model registry match`. Distinct from a skill `No registry match`.

**Runtime availability**:
Whether local evidence proves the current runtime cannot select a profile's exact model and effort: `unavailable` or `unknown`. Distinct from skill availability.
