# 📐 Gauge

> **Stop over-planning 2-line fixes. Stop under-planning auth migrations.**

Pre-planning engagement and routing skill for AI-native software engineering.

[![Skills](https://img.shields.io/badge/skills-98kb%2Fgauge-blue?style=flat-square)](https://github.com/98kb/gauge)
[![Inspect AI](https://img.shields.io/badge/evals-Inspect%20AI%20(14%20scenarios)-success?style=flat-square)](evals/inspect-ai/README.md)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](https://opensource.org/licenses/MIT)

---

Software engineering agents suffer from two mirrored failure modes:

1. **The Under-Planning Trap (`G0` Fallacy):** Leaping straight into code on high-consequence tasks (auth boundaries, data migrations, domain refactors), causing silent regressions and rollback chaos.
2. **The Over-Planning Tax (Bureaucratic Drag):** Generating 40-page PRDs and 15 tickets for a 3-line UI label fix or routine dependency bump.

**Gauge sits immediately before planning.** Given an intent, repository context, and available tools, Gauge answers:

> *"What exact process should produce the plan for this intent, or should a separate planning step be skipped?"*

The output is an executable **Planning Recipe**: a base topology (`G0`–`G3`), behavioral modifiers, resolved skill bindings, and copy-paste-ready **launch packets** with strict execution boundaries.

---

## Installation & Usage

Install Gauge into any agent workspace with the `skills` CLI:

```bash
npx skills add 98kb/gauge
```

Compatible with Claude Code, Cursor, Windsurf, Codex, Gemini CLI / Antigravity, and any runtime supporting the open Agent Skills standard.

### Invoking Gauge

Gauge explicitly requires human invocation (`disable-model-invocation: true` / `allow_implicit_invocation: false`)—models cannot trigger it autonomously. Run it directly as a slash command when sizing up an effort before planning or implementing:

```text
# High-consequence architecture & boundaries
/gauge the effort required to replace payment gateway
/gauge updating token-expiry handling at the auth boundary

# Domain & product features
/gauge an audit logging module with tenant isolation
/gauge team invites with custom RBAC permissions

# Multi-session or exploratory work
/gauge a multi-session notification engine overhaul
/gauge whether we need a spike before integrating third-party webhooks

# Bounded fixes & conventional tasks
/gauge updating the checkout CTA label and styling
```

---

## The Four Topologies

Topology codes define workflow structure and persistence requirements—**not** difficulty or story points:

| Code | Topology | Contract | When to Use | Typical Pipeline |
| :--- | :--- | :--- | :--- | :--- |
| **`G0`** | **Direct** | Skip planning. Hand intent and guardrails straight to implementation. | Bounded, conventional fixes with obvious verification seams. | `Implementation launch packet` |
| **`G1`** | **Handoff** | Produce a bounded context package without an interactive interview. | Settled decisions; context is discoverable in repo/docs; fits one session. | `context handoff` → `implementation` |
| **`G2`** | **Interactive** | Elicit human judgement before generating an implementation handoff. | Domain decisions, trade-offs, permission models, or learning goals. | `interactive elicitation` → `context handoff` → `implementation` |
| **`G3`** | **Navigated** | Preserve decisions and decomposition across multiple persistent sessions. | Multi-session builds. Split into **G3-A** (route decided) or **G3-B** (route foggy). | `decision map` → `specification` → `tickets` → `sessions` |

> [!NOTE]
> Work topology and human collaboration posture are separate axes. Human expertise shifts modifiers, checkpoints, and explanation depth; it only changes topology when it changes where essential knowledge lives.

---

## Behavioral Modifiers

Modifiers tune agent posture and guardrails without altering the underlying topology:

| Modifier | Agent Posture |
| :--- | :--- |
| `Educational` | Explains unfamiliar concepts and trade-offs before requesting decisions in named domains. |
| `Delegated judgement` | Selects conventional defaults autonomously; explicitly logs assumptions. |
| `Human-decision` | Presents options with recommendations and pauses for explicit human sign-off. |
| `High-assurance` | Demands failure mode analysis, rollback strategies, and strict verification seams. |
| `Discovery-first` | Resolves empirical or external unknowns via spikes/prototyping before locking decisions. |
| `Checkpointed` | Returns to the human at defined milestones rather than only on completion. |
| `Exception-only` | Runs autonomously within guardrails; interrupts only when escalation triggers are hit. |

---

## Anatomy of a Planning Recipe

When invoked, Gauge reconnoitres the task and emits a structured recipe:

```markdown
# Gauge result

## Verdict
- Topology: G2 Interactive
- Modifiers: Human-decision (role hierarchy), High-assurance (security boundary)
- Confidence: High

## Why this fits
RBAC data models already exist in the codebase, but tenant-isolation boundaries 
and invitation expiry policies require human product decisions.

## Human collaboration contract
- Human decides: Role hierarchy, invite expiration, invitation revocation rules
- Agent may decide: DB migration syntax, token generation utilities
- Checkpoints: After permission model sign-off

## Resolved planning recipe

### Step 1 — Elicit authorization semantics
- Skill: grill-me
- Availability: installed
- Invocation: /grill-me
- Inputs: Intent and src/auth/roles.ts
- Expected output: docs/decisions/0012-invite-rbac.md
- Exit condition: Human confirms permission hierarchy

#### Launch packet
Role: grill-me as step 1 of Gauge planning recipe.
Intent: "Add team invites with granular role assignments"
Context: Existing RBAC in src/auth/roles.ts. Tenant isolation in src/db/schema.prisma.
Constraints: Do not modify global superadmin permissions.
Output: docs/decisions/0012-invite-rbac.md
Boundary: Plan; do not implement.

## Implementation handoff
Implementation agent consumes docs/decisions/0012-invite-rbac.md as a G1 run.

## Escalate or re-Gauge if
- Existing user schema lacks multi-tenant tenant_id scoping.
- External SSO or SAML integration is requested.
```

---

## Ecosystem & Skill Registry

Gauge decouples routing capabilities (`interactive elicitation`, `ticket decomposition`, `context handoff`) from concrete implementations.

Currently, the default registry is seeded with [Matt Pocock's planning skills](https://github.com/mattpocock/skills):

- [`handoff`](https://github.com/mattpocock/skills/tree/main/skills/handoff) — Bounded context packages for single-run tasks (`G1`).
- [`grill-me`](https://github.com/mattpocock/skills/tree/main/skills/grill-me) / [`grill-with-docs`](https://github.com/mattpocock/skills/tree/main/skills/grill-with-docs) — Interactive elicitation interviews (`G2`).
- [`to-spec`](https://github.com/mattpocock/skills/tree/main/skills/to-spec) & [`to-tickets`](https://github.com/mattpocock/skills/tree/main/skills/to-tickets) — Durable specifications and tracer-bullet task decomposition (`G3-A`).
- [`wayfinder`](https://github.com/mattpocock/skills/tree/main/skills/wayfinder) — Multi-session navigated state maps (`G3-B`).

### Expanding Beyond One Creator

While Matt Pocock's skills form our initial baseline, **Gauge is designed to be multi-ecosystem**. We are actively expanding the registry to include top-tier skills from other creators across the AI engineering community—pairing the right specialized skill to each task to produce richer recipes so downstream agents can truly cook.

Contributions and proposed bindings are welcome in [`references/planning-registry.md`](references/planning-registry.md).

---

## Evaluation & Rigor

Gauge's routing logic is deterministically and behaviorally benchmarked across 14 scenarios using the UK AI Safety Institute's [Inspect AI](https://inspect.aisi.org.uk/) framework:

- **Deterministic checks:** Schema adherence, absence of arbitrary complexity scores, rigid non-execution bounds (`Plan; do not implement`).
- **LLM-judged rubrics:** Routing accuracy, appropriate human modeling without stereotyping, and leak prevention.

See [`evals/inspect-ai/README.md`](evals/inspect-ai/README.md) and [`docs/INSPECT_AI_GAUGE_EVAL_SETUP.md`](docs/INSPECT_AI_GAUGE_EVAL_SETUP.md) for benchmark setup and reproduction.

---

## Documentation

- [Skill Specification (`SKILL.md`)](SKILL.md)
- [Routing Model (`references/routing-model.md`)](references/routing-model.md)
- [Planning Registry (`references/planning-registry.md`)](references/planning-registry.md)
- [Recipe Contract (`references/recipe-contract.md`)](references/recipe-contract.md)
- [Architecture & ADRs (`docs/adr/`)](docs/adr/)

---

## License

[MIT](https://opensource.org/licenses/MIT)
