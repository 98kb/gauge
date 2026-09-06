<div align="center">

# 📐 Gauge

**Pre-planning engagement and routing skill for AI-native software engineering.**

*Right-sized planning for agentic workflows — prevent both under-planning and ritualistic over-planning.*

[![Skills](https://img.shields.io/badge/skills-98kb%2Fgauge-blue?style=flat-square&logo=npm)](https://github.com/98kb/gauge)
[![Inspect AI](https://img.shields.io/badge/evals-Inspect%20AI%20(14%20scenarios)-success?style=flat-square&logo=python)](evals/inspect-ai/README.md)
[![Topologies](https://img.shields.io/badge/topologies-G0%20%7C%20G1%20%7C%20G2%20%7C%20G3-orange?style=flat-square)](#-the-four-topologies)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](https://github.com/98kb/gauge)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](https://github.com/98kb/gauge/pulls)

<br />

[Features](#-features) • [Installation](#-installation) • [How it Works](#-how-it-works) • [Topologies](#-the-four-topologies) • [Modifiers](#-behavioral-modifiers) • [Example Recipe](#-anatomy-of-a-planning-recipe) • [Evals](#-evals--rigor) • [Docs](#-documentation)

<br />

</div>

---

## ⚡ The Problem: Two Failure Modes of Agentic Planning

Every software engineering agent eventually falls into one of two traps:

1. **The Under-Planning Trap (G0 Fallacy):** Leaping straight into code on high-consequence tasks (like modifying an auth boundary, running a database migration, or restructuring domain models) without human alignment, causing silent regressions, security leaks, and rollback chaos.
2. **The Over-Planning Tax (Bureaucratic Drag):** Generating 40-page markdown PRDs, architecture decision trees, and 15 Jira tickets for a bounded 3-line UI label fix or routine dependency bump.

**Gauge sits immediately before planning.** Given an intent, repository terrain, human context, and a curated registry of planning skills, Gauge asks:

> *"What exact process should produce the plan for this intent, or should a separate planning step be skipped?"*

The answer is an executable **Planning Recipe**: a base topology, dynamic behavioral modifiers, a sequence of resolved skills, and copy-paste-ready **launch packets** to hand off directly to your favorite agent.

---

## ✨ Features

- 🎯 **Four Disciplined Topologies (`G0`–`G3`):** Intelligently routes between Direct execution (`G0`), Bounded context handoffs (`G1`), Interactive elicitation (`G2`), or Navigated multi-session state maps (`G3`).
- 🛡️ **Assurance Floor:** High-risk vectors (security, migrations, public API compatibility) automatically raise verification and review rigor without artificially bloating session persistence.
- 📦 **Copy-Paste Launch Packets:** Emits isolated, prompt-ready packets for every step featuring rigid `Plan; do not implement` boundaries, confirmed constraints, and escalation triggers.
- 🎛️ **Behavioral Modifiers:** Dynamically dials agent posture (`Educational`, `High-assurance`, `Delegated judgement`, `Human-decision`, `Discovery-first`, `Checkpointed`, `Exception-only`).
- 🧠 **Human-in-the-Loop Contract:** Explicitly establishes decision ownership: what the human decides, what the agent may decide with defaults, and where checkpoints occur.
- 🧪 **Inspect AI Evaluation Suite:** Backed by 14 real-world behavioural fixtures validated with the UK AI Safety Institute's [Inspect AI](https://inspect.aisi.org.uk/) framework.
- 🔌 **Pluggable Ecosystem:** Native out-of-the-box bindings to [Matt Pocock's skills](https://github.com/mattpocock/skills) (`handoff`, `grill-me`, `to-spec`, `to-tickets`, `wayfinder`), with provider-neutral routing abstractions.

---

## 🚀 Installation

Install Gauge into your workspace with the `skills` CLI:

```bash
npx skills add 98kb/gauge
```

Compatible with **Claude Code**, **Codex**, **Cursor**, **Windsurf**, **Gemini CLI / Antigravity**, and any runtime supporting the open Agent Skills standard.

---

## 🔍 How it Works

```
                     ┌────────────────────────┐
                     │   Human / Task Intent  │
                     └───────────┬────────────┘
                                 │
                     ┌───────────▼────────────┐
                     │     Gauge Routing      │
                     │  • Intent framing      │
                     │  • Bounded repository  │
                     │  • Knowledge location  │
                     │  • Human model         │
                     └───────────┬────────────┘
                                 │
           ┌──────────────┬──────┴───────┬──────────────┐
           ▼              ▼              ▼              ▼
       ┌───────┐      ┌───────┐      ┌───────┐      ┌───────┐
       │  G0   │      │  G1   │      │  G2   │      │  G3   │
       │Direct │      │Handoff│      │Inter- │      │Navi-  │
       │       │      │       │      │active │      │gated  │
       └───┬───┘      └───┬───┘      └───┬───┘      └───┬───┘
           │              │              │              │
           └──────────────┴──────┬───────┴──────────────┘
                                 │
                      + Behavioral Modifiers
                      + Registry Binding
                                 │
                     ┌───────────▼────────────┐
                     │    Planning Recipe     │
                     │  • Verdict & Contract  │
                     │  • Step 1..N Packets   │
                     │  • Escalation Triggers │
                     └────────────────────────┘
```

Gauge executes a 9-step reconnaissance pipeline before emitting the recipe and stopping:
1. **Preserve & frame intent:** Captures verbatim wording, success state, and human constraints without artificially expanding scope.
2. **Reconnoitre repository:** Inspects codebase surfaces, prior art, verification seams, and blast radius.
3. **Build human model:** Assesses task-specific familiarity, decision ownership, and learning objectives (without personal categorization).
4. **Locate unresolved knowledge:** Maps unknowns to human tacit knowledge, local documentation, or external discovery.
5. **Ask routing-critical questions:** Clarifies only what could change topology or decision rights; saves the full design interview for downstream planning.
6. **Select dominant topology:** Evaluates G0 through G3 conditions.
7. **Attach modifiers:** Appends behavioural contracts (e.g. `High-assurance`, `Educational`).
8. **Resolve registry bindings:** Identifies smallest sufficient skill chain and generates isolated launch packets.
9. **Emit recipe and halt:** Leaves execution to downstream agents.

---

## 🧭 The Four Topologies

Topology codes represent workflow structure and persistence requirements, **not** difficulty or complexity scores:

| Code | Topology | Contract | When to Use | Typical Pipeline |
| :--- | :--- | :--- | :--- | :--- |
| **`G0`** | **Direct** | Skip planning entirely. Proceed immediately to verified implementation. | Bounded, conventional changes with clear verification (e.g. rename a UI label, update a test case). | `Implementation launch packet` |
| **`G1`** | **Handoff** | Produce a bounded context package without an interactive human interview. | Settled decisions, context can be harvested from repo/docs, fits one coherent agent run. | `context handoff` → `implementation` |
| **`G2`** | **Interactive** | Elicit tacit human knowledge or judgement before creating implementation handoff. | Domain decisions, trade-offs, permissions, or learning goals require human input. | `interactive elicitation` → `context handoff` → `implementation` |
| **`G3`** | **Navigated** | Preserve decisions and decomposition across multiple persistent agent sessions. | Multi-session builds. Split into **G3-A** (route decided) or **G3-B** (route foggy). | `decision map` → `specification` → `tickets` → `sessions` |

> [!NOTE]
> Work topology and human collaboration posture are separate axes. Human expertise moves modifiers, checkpoints, and explanation depth; it only changes topology when it changes where knowledge lives.

---

## 🎛️ Behavioral Modifiers

Modifiers alter agent behavior during planning or execution without altering the base topology:

| Modifier | Contract & Agent Behavior |
| :--- | :--- |
| `Educational` | Explains unfamiliar concepts and trade-offs before requesting decisions in named domains. |
| `Delegated judgement` | Grants agent authority to choose conventional defaults; requires explicit recording of assumptions. |
| `Human-decision` | Presents options with recommendations and pauses for explicit human sign-off at named boundaries. |
| `High-assurance` | Demands failure analysis, verification seams, rollback strategy, and specialist verification in final plan. |
| `Discovery-first` | Resolves empirical or external unknowns via primary research or prototype before locking decisions. |
| `Checkpointed` | Returns to the human at explicit milestones rather than only at terminal step completion. |
| `Exception-only` | Operates fully autonomously within guardrails; interrupts only when escalation triggers are hit. |

---

## 📋 Anatomy of a Planning Recipe

When Gauge runs, it emits a standardized, actionable Markdown recipe:

```markdown
# Gauge result

## Verdict
- Topology: G2 Interactive
- Variant: none
- Modifiers: Human-decision (permissions, notification rules), High-assurance
- Confidence: High

## Why this fits
The core data model is established in the repository, but authorization boundaries 
and notification failure semantics are tacit human product decisions. 
External email provider integration requires high-assurance verification seams.

## Human collaboration contract
- Human decides: Permission matrix, fallback email delivery rules
- Agent may decide: Database schema naming, retry backoff intervals
- Explain before deciding: none
- Checkpoints: After permission model selection

## Resolved planning recipe

### Step 1 — Elicit authorization and delivery semantics
- Skill: grill-with-docs
- Dependencies: grilling, domain-modeling
- Availability: installed
- Invocation: /grill-with-docs
- Inputs: Intent and src/auth/roles.ts
- Expected output: docs/decisions/0012-invite-auth.md
- Exit condition: Human confirms permissions and notification semantics
- Next handoff: Step 2 receives decision record

#### Launch packet
Role: grill-with-docs as step 1 of a Gauge planning recipe.

Intent, verbatim:
"Add organization team invites with granular role assignments"

Destination: Settled invite flow with permissions matrix and delivery fallback.
Context:
- Environment: git checkout on main
- Findings: Existing RBAC located in src/auth/roles.ts

Constraints and exclusions:
- Do not modify existing superadmin scopes.

Human collaboration:
- Human decides: Permission matrix, notification rules
- You may decide: Schema column names

Output: docs/decisions/0012-invite-auth.md
Done when: Decision record written and approved by human.
Boundary: Plan; do not implement.

## Implementation handoff
Implementation agent receives the decision record and executes as G1 run.

## Escalate or re-Gauge if
- Existing user model lacks multi-tenant tenant_id scoping.
- Human requests external SSO integration.
```

---

## 🧪 Evals & Rigor

Gauge is built to production standards and tested using [Inspect AI](https://inspect.aisi.org.uk/), the evaluation framework developed by the UK AI Safety Institute (AISI).

Our evaluation harness isolates 14 diverse behavioural fixtures:
- **Mechanical Checks (Deterministic):** Validates schema adherence, zero complexity estimation scores, invariant availability states, and non-execution bounds.
- **Judge Checks (LLM Rubrics):** Evaluates routing fidelity, appropriate human modeling without stereotyping, and lack of unauthorized implementation.

### Quick Start for Evals

```bash
cd evals/inspect-ai

# 1. Setup python virtual environment
./run.sh setup

# 2. Run offline validation (no model calls, zero cost)
./run.sh check

# 3. Run 3-case smoke test
./run.sh smoke --model anthropic/claude-3-5-sonnet-20241022

# 4. Run full 14-case evaluation suite
./run.sh gauge --model anthropic/claude-3-5-sonnet-20241022
```

See [`evals/inspect-ai/README.md`](evals/inspect-ai/README.md) and [`docs/INSPECT_AI_GAUGE_EVAL_SETUP.md`](docs/INSPECT_AI_GAUGE_EVAL_SETUP.md) for full benchmark documentation.

---

## 📁 Repository Layout

```text
gauge/
├── SKILL.md                 # Canonical skill definition & instructions
├── agents/
│   └── openai.yaml          # Runtime metadata & invocation policy
├── references/
│   ├── routing-model.md     # Topology criteria, human model & modifiers
│   ├── planning-registry.md # Curated skill catalog & bindings
│   ├── recipe-contract.md   # Result schema, launch packet templates & confidence
│   └── evaluation-scenarios.md # Behavioral test fixtures
├── evals/
│   ├── README.md            # Eval harness overview
│   └── inspect-ai/          # Inspect AI task definitions and runner scripts
└── docs/
    ├── gauge-implementation-spec.md # Complete architectural specification
    └── adr/                 # Architecture Decision Records
```

---

## 🔗 Ecosystem & Lineage

Gauge was developed by [98kb](https://github.com/98kb) as part of the next-generation product planning pipeline in [`98kb/skills`](https://github.com/98kb/skills). It has been extracted into this dedicated repository to serve as a standalone, universal pre-planning router for any AI-native coding environment.

Out of the box, Gauge binds directly to [Matt Pocock's skills repository](https://github.com/mattpocock/skills):
- [`handoff`](https://github.com/mattpocock/skills/tree/main/skills/handoff): Bounded context handoffs for single agent runs.
- [`grill-me`](https://github.com/mattpocock/skills/tree/main/skills/grill-me) / [`grill-with-docs`](https://github.com/mattpocock/skills/tree/main/skills/grill-with-docs): Interactive elicitation interviews.
- [`to-spec`](https://github.com/mattpocock/skills/tree/main/skills/to-spec): Synthesizing durable project specifications.
- [`to-tickets`](https://github.com/mattpocock/skills/tree/main/skills/to-tickets): Task decomposition and tracer-bullet tickets.
- [`wayfinder`](https://github.com/mattpocock/skills/tree/main/skills/wayfinder): Multi-session navigated decision maps.

## 📄 License

Open source under the [MIT License](https://opensource.org/licenses/MIT).
