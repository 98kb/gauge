---
status: accepted
date: 2026-09-11
---

# Model profiles are single, advisory, and capability-bound

Gauge recommends one **model profile**—a canonical pinned model ID plus one reasoning-effort value that model supports—at every execution boundary of a recipe. Profiles come from a separate, human-edited model registry that initially holds Anthropic profiles only. Reasoning effort is a model control (Anthropic's `output_config.effort`); it is never an estimate of implementation time, cost, size, or complexity, which Gauge still forbids.

## Decision

- **Execution boundaries.** Tracker setup when present, every planning step, the G0 implementation step, and the non-G0 **Implementation handoff**. Dependency skills run inside their entry point's session and carry no profile; human-only installation actions carry none. G3 implementation sessions share the handoff's single profile.
- **One profile.** Each boundary resolves exactly one profile or reports `No model registry match: <binding key>`. No ordered fallbacks; Gauge never substitutes a model or lowers effort.
- **Profile shape.** A canonical pinned ID, never a convenience alias, and exactly one effort value the model supports. A model without effort support (Haiku 4.5 on 2026-09-11) cannot form a profile.
- **Binding.** Profiles bind to a provider-neutral capability, never to the selected skill. `implementation` is an explicit capability covering both G0 and the non-G0 handoff. `High-assurance` is the only modifier that affects binding: a High-assurance boundary requires an explicit capability + `High-assurance` binding, and without one reports `No model registry match: <capability> + High-assurance`; it never falls back to the base binding. Skill and model resolution are independent: `No registry match` or `No planning skill` does not block a profile, and a model gap does not affect the skill binding.
- **Advisory.** Recommendations, including those repeated in launch packets, are advice across harnesses. Gauge never claims a profile was applied or enforced.
- **Runtime availability.** The recommendation is always retained exactly. Beside it Gauge reports `unavailable` only when local, read-only evidence proves the exact pair cannot be selected—and names that evidence (e.g. an `availableModels` exclusion, a `maxEffortLevel` cap below the effort, a harness version below the model's minimum)—and `unknown` otherwise. Gauge never reports `available`: org and account access is enforced server-side, and the recipe usually runs in another session. No network or provider-API calls. A runtime mismatch is never a registry gap and never `n/a`.

## Consequences

- `references/model-registry.md` becomes a fifth reference. Spec §7 lists it; §19's deferred "multiple provider registries" means additional skill-ecosystem registries, not this one.
- `routing-model.md` stops calling `implementation` a non-capability; the planning registry's `implementation launch packet` binding key becomes `implementation`.
- The recipe contract, model-registry parser, deterministic checks, controls, and judged scenarios evolve together.
- Implementation is gated on a separate maintainer approval of the initial profiles and the capability × {base, `High-assurance`} mapping; neither is inferred from Anthropic's suitability prose.

## Considered options

Rejected: storing profiles in the existing planning registry (cheaper until a second provider exists, but mixes model and skill data); ordered fallbacks; enforcement gated on runtime proof; skill-bound or skill+capability binding; modifiers other than `High-assurance` affecting binding; base-binding fallback for High-assurance; effort-less profiles; an `available` state, or no runtime label; `n/a` or a registry gap for a runtime mismatch.

Facts as of 2026-09-11: [Anthropic model-registry research](../research/anthropic-model-registry.md).
