# Gauge Skill — Implementation Specification

**Status:** MVP implementation handoff  
**Date:** 2026-09-04  
**Target:** A portable agent skill named `gauge`  
**Authority:** This specification captures the current product decisions. Implement the skill; do not reopen product design unless a contradiction makes implementation impossible.

## 1. Executive summary

Gauge is a pre-planning engagement and routing skill for an AI-native software-development lifecycle.

It examines:

- the human's intent and desired destination;
- the relevant environment or repository;
- the shape, uncertainty, consequences, and continuity of the work;
- the human's task-specific knowledge, desired involvement, learning goal, and ability to evaluate mistakes; and
- the planning skills available or recommendable through Gauge's curated registry.

Gauge then produces a **resolved, executable planning recipe**. The recipe says exactly how planning should happen, which skill or sequence of skills should be used, how the human should participate, what each step should produce, and when the workflow should escalate.

Gauge does **not** create the substantive plan and does **not** implement the intent.

The MVP registry is deliberately limited to the planning-relevant skills in [Matt Pocock's skills repository](https://github.com/mattpocock/skills). Gauge's conceptual vocabulary must remain provider-neutral even though the initial registry is not.

## 2. Product contract

### 2.1 Core question

Gauge answers:

> Given this intent, environment, human, and available planning-skill registry, what exact process should be used to produce an appropriate plan—or should a separate planning step be skipped?

### 2.2 Primary output

The primary output is a **planning recipe** that is both:

1. human-readable, so the user can understand and override the recommendation; and
2. agent-executable, so the recipe or its per-step launch packets can be used directly as prompts for planning agents or skills.

### 2.3 Success condition

Gauge is finished when the user or an orchestration agent knows:

- whether a distinct planning phase is needed;
- which exact skill or skills to invoke;
- in what order to invoke them;
- what context and prompt to give each one;
- what role the human plays;
- what artifact should emerge;
- how that artifact reaches implementation; and
- what findings require escalation or re-Gauging.

The recipient must not need to invent another prompt or decide how planning itself should be conducted.

## 3. Goals

1. Prevent both under-planning and ritualistic over-planning.
2. Match the planning workflow to the work and to the specific human engaging with it.
3. Give exact, practical skill recommendations rather than theoretical categories.
4. Preserve continuity between intent, planning, and implementation agents.
5. Make the output directly reusable as a seed prompt or orchestration recipe.
6. Make assumptions, human decision rights, and escalation conditions visible.
7. Remain useful when recommended skills are not currently installed by providing exact installation guidance.
8. Keep the architecture open to future registries without implementing that extensibility in the MVP.

## 4. Non-goals

Gauge must not:

- produce the substantive product, architecture, or implementation plan;
- decompose the intended build into implementation tasks itself;
- implement, modify, or execute the intended change;
- automatically invoke a planning or implementation skill;
- install skills or mutate user configuration without an explicit later request;
- provide time, cost, story-point, or person-day estimates as its primary result;
- assign a permanent `expert` or `novice` label to the human;
- research the human on the public internet or infer sensitive personal traits;
- become a general-purpose router over every engineering skill;
- discover arbitrary third-party skill ecosystems in the MVP;
- duplicate Matt Pocock's `ask-matt` router or recommend it as a planning step;
- treat Wayfinder as the default for every large change; or
- save or update a planning recipe as a file unless the user requests an artifact.

## 5. Terminology and roles

### 5.1 Intent

The human's desired destination, including known outcomes, constraints, exclusions, and motivations. The initial wording must be retained faithfully in the recipe; Gauge may clarify it but must not silently replace it.

### 5.2 Engaging agent

The agent running Gauge. It researches the intent, task environment, and task-relevant human context. It chooses the planning topology and compiles the planning recipe.

### 5.3 Planning agent

An optional agent or skill that executes one step of the recipe and produces a planning artifact, decisions, specification, map, or ticket set.

### 5.4 Implementation agent

The agent that executes directly from the intent for G0, or consumes the artifact produced by the planning workflow for other routes.

### 5.5 Planning topology

The dominant shape of the workflow: Direct, Handoff, Interactive, or Navigated. It is not a linear measure of general difficulty.

### 5.6 Modifier

A collaboration or assurance instruction added to the base topology, such as Educational or High-assurance.

### 5.7 Recipe template

A provider-neutral composition of capabilities, such as:

`interactive elicitation -> durable specification -> implementation handoff`

### 5.8 Resolved recipe

A recipe template bound to exact skills and invocation instructions from the active registry.

### 5.9 Launch packet

A copy-paste-ready seed prompt for one particular skill or agent in a resolved recipe.

## 6. Locked design decisions

### 6.1 No numerical complexity score

Do not calculate or display a score out of 10, 100, T-shirt size, or story points. Such a score would conflate implementation magnitude, uncertainty, risk, human knowledge, and persistence.

Gauge selects a workflow topology and attaches modifiers.

### 6.2 Base topologies

| Code | Name | Contract |
| --- | --- | --- |
| G0 | Direct | Skip a separate planning phase. Hand the intent and explicit guardrails directly to an implementation agent. |
| G1 | Handoff | Produce a bounded context/specification handoff without a substantive human interview, normally for one coherent implementation run. |
| G2 | Interactive | Elicit human-held knowledge or judgement before creating the implementation handoff. |
| G3 | Navigated | Preserve decisions and decomposition across multiple planning or implementation sessions. Use Wayfinder only when the route remains foggy; use specification and tickets when the route is already decided. |

The code is a compact label, not a claim that G3 is always riskier or harder than G2.

### 6.3 Work topology and collaboration posture are separate

Human expertise must not mechanically move an intent up or down the Gauge scale. It usually changes:

- decision ownership;
- explanation depth;
- checkpoint frequency;
- evidence requirements; and
- escalation rules.

Human context changes the base topology only when it changes where necessary knowledge resides, whether important decisions require interaction, or whether the human can responsibly delegate those decisions.

### 6.4 V1 registry boundary

The bundled registry contains only verified, planning-relevant skills from Matt Pocock's collection. Generic capability names must not contain the author or ecosystem name, so additional registries can be added later without changing the routing model.

### 6.5 Generate, do not execute

Gauge emits a recipe and stops. It does not invoke, install, or execute the selected skills. The user may pass the whole recipe to an orchestration agent or use the individual launch packets manually.

## 7. Recommended skill package

Implement the following minimal structure:

```text
gauge/
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
`-- references/
    |-- routing-model.md
    |-- planning-registry.md
    |-- recipe-contract.md
    |-- model-registry.md
    `-- evaluation-scenarios.md
```

Do not add scripts, assets, a README, a changelog, or placeholder files in the MVP.

### 7.1 `SKILL.md`

Keep the entrypoint concise. It must contain:

- purpose and boundary;
- the high-level runtime workflow;
- the rule that Gauge produces a recipe rather than a plan;
- the rule to inspect only task-relevant human context;
- the four base topologies;
- the stopping condition; and
- explicit links telling the agent when to read each reference.

Recommended frontmatter:

```yaml
---
name: gauge
description: Assess an intent before planning, choose a Direct, Handoff, Interactive, or Navigated workflow, and produce an executable planning recipe using the configured skill registry. Use when the user asks to gauge an effort, decide how much planning it needs, choose a planning workflow, or generate a seed prompt for planning. Do not use merely because the user directly asks to implement or has already chosen a planning method.
---
```

Keep normal automatic discovery enabled; the description is narrow enough to prevent invocation on every implementation request.

### 7.2 `agents/openai.yaml`

Generate valid UI metadata consistent with the skill:

```yaml
interface:
  display_name: "Gauge"
  short_description: "Turn intent into an executable planning recipe"
  default_prompt: "Gauge this intent and produce an executable planning recipe."
```

Do not add an explicit-only invocation policy unless the target environment requires it.

### 7.3 References

- `routing-model.md` owns detailed routing criteria, human-context rules, knowledge-location analysis, and modifiers.
- `planning-registry.md` is the live, human-editable MVP registry. It owns verified skill metadata, dependencies, installation guidance, and recipe bindings.
- `recipe-contract.md` owns the exact output schema and launch-packet template.
- `evaluation-scenarios.md` owns behavioural fixtures and expected invariants, not brittle wording assertions.
- `model-registry.md` is the separate, human-edited model registry ([ADR 0017](adr/0017-model-profiles-are-single-advisory-and-capability-bound.md)). It owns the Anthropic model profiles, their capability × {base, `High-assurance`} bindings, the `No model registry match` outcome, and the runtime-availability evidence rules.

Avoid duplicating the same rule across the entrypoint and references.

## 8. Runtime workflow

Gauge must follow this sequence.

### Step 1: Preserve and frame the intent

Capture:

- the original intent;
- the destination or success state;
- explicit constraints and exclusions;
- whether delivery, learning, or both are desired; and
- any planning method the human has already required or ruled out.

Do not reinterpret a request into a larger product initiative.

### Step 2: Perform bounded task reconnaissance

Inspect the repository, project documentation, issue tracker context, or supplied artifacts only far enough to route the work. Look for:

- affected subsystems and coupling;
- existing patterns or prior art;
- reversibility and rollback constraints;
- security, data, compatibility, or production consequences;
- available verification seams;
- whether the route is already known;
- whether work can fit one coherent implementation run; and
- whether decisions must survive across sessions.

Do not produce a full architecture survey, solve design questions, draft tickets, or start implementation. If the necessary environment is unavailable, state the resulting assumption.

### Step 3: Build a task-specific human model

Assess only information that can change the recipe:

- destination knowledge: can the human recognize the correct outcome?
- route/domain knowledge: do they understand relevant implementation trade-offs?
- terrain familiarity: do they know this repository, organization, or operational environment?
- evaluation ability: can they detect plausible errors or unsafe assumptions?
- decision ownership: which choices do they want to make personally?
- delegation posture: which choices may the agent make using conventional defaults?
- learning goal: is understanding part of the desired outcome?
- oversight availability: how much review attention can the human provide?

Use this evidence order:

1. explicit statements in the current request or conversation;
2. explicit user, project, or repository profile documents supplied to the agent;
3. directly observed work, decisions, or artifacts relevant to this task;
4. clearly labelled inference.

Never search externally for information about the person. Never infer sensitive traits, personality, intelligence, or broad competence. Never quiz the human merely to prove expertise.

Expose only consequential assumptions in the result. Phrase them narrowly, for example:

> I am assuming you can review the TypeScript design but want security implications explained before you approve them.

Do not say:

> You are a novice developer.

### Step 4: Locate unresolved knowledge

Classify each consequential unknown by where its answer can come from:

| Location | Routing implication |
| --- | --- |
| Current human | Add an Interactive step or Human-decision modifier. |
| Repository or local documentation | Research it during planning; do not ask the human. |
| Established external source | Add a Discovery-first/Research step. |
| Planning agent's conventional judgement | Delegate explicitly and require assumptions to be recorded. |
| Another stakeholder | State that stakeholder input is required; do not let the current agent impersonate them. |
| Nobody yet knows | Add research or prototype work before locking the plan. |

### Step 5: Ask only routing-critical questions

Ask the smallest useful set of questions when an answer could materially change:

- the base topology;
- decision ownership;
- whether an Educational modifier is required;
- whether the work can be delegated safely; or
- whether the workflow must persist across sessions.

One concise batch is usually sufficient. Do not begin the full interview that belongs to `grill-me`, `grill-with-docs`, or Wayfinder.

If the user has already supplied enough context, ask nothing.

### Step 6: Select the dominant topology

Use the routing model in Section 9.

### Step 7: Attach modifiers

Use only modifiers that change agent behaviour. Do not decorate every recipe with every plausible concern.

### Step 8: Resolve the recipe

Read `planning-registry.md`, choose the smallest sufficient skill sequence, check whether each skill is detectable in the current environment, expand dependencies, and construct launch packets.

Do not recommend `ask-matt`; Gauge itself owns routing.

If the registry contains no suitable skill for a required capability, do not force-fit the closest entry. Mark that recipe step as `No registry match`, describe the missing capability precisely, and state that the MVP catalog cannot fully resolve the recipe. Do not invent a third-party recommendation or a generic fallback protocol.

Independently of skill resolution, read `model-registry.md` and give every execution boundary one advisory model profile, per [ADR 0017](adr/0017-model-profiles-are-single-advisory-and-capability-bound.md). The boundaries are tracker setup, each planning step, the G0 implementation step, and the non-G0 Implementation handoff. Resolve by capability, plus `High-assurance` when attached, and report `No model registry match` where no binding exists. Label runtime availability `unavailable` (with named local evidence) or `unknown`. `references/recipe-contract.md` defines the fields.

### Step 9: Emit the recipe and stop

Follow `recipe-contract.md`. Do not immediately run the first planning step. The final line may tell the user that the recipe or an individual launch packet can be pasted into the next agent.

## 9. Routing model

### 9.1 Preliminary destination check

If a meaningful destination cannot yet be named, use an Interactive recipe to clarify it. Add `Discovery-first` if facts or experiments are required before the destination can be settled.

Do not call an undefined idea G3 merely because it is broad.

### 9.2 Select G3 — Navigated

Choose G3 when decisions, planning state, or implementation decomposition must survive multiple fresh agent sessions.

Then choose one of two G3 variants:

#### G3-A: Route already decided

Use when substantive decisions are settled but the build is too large for one implementation session.

Default recipe:

`to-spec -> to-tickets -> implementation sessions`

Do not add Wayfinder.

#### G3-B: Route still foggy

Use when the destination can be named, but the route contains interdependent decisions or investigations that cannot fit one planning session.

Default recipe:

`wayfinder -> to-spec -> to-tickets -> implementation sessions`

Wayfinder is justified by both persistence and fog, not by size alone.

### 9.3 Select G2 — Interactive

Choose G2 when one or more material decisions depend on:

- tacit knowledge held by the human;
- preferences or trade-offs the human should own;
- ambiguous domain language;
- a learning goal that requires understanding before approval; or
- a decision the human is not yet ready to delegate.

The planning can normally be settled in one interactive planning session.

Default bindings:

- no repository or non-code intent: `grill-me` with dependency `grilling`;
- repository-backed software change: `grill-with-docs` with dependencies `grilling` and `domain-modeling`;
- if a fresh implementation session needs the settled context: append `handoff`;
- if the implementation spans sessions: classify the dominant topology as G3 and include the appropriate G2 step within its recipe.

### 9.4 Select G1 — Handoff

Choose G1 when:

- the destination and material decisions are sufficiently settled;
- the agent can obtain remaining facts from the environment;
- no substantive human interview is required;
- the work benefits from a stable context package; and
- implementation can normally proceed as one coherent run.

Default binding: `handoff`, tailored to the implementation session.

Do not use `to-spec` merely to make G1 feel more formal. In the current Matt Pocock flow, `to-spec` earns its cost primarily when decisions must survive a multi-session build.

### 9.5 Select G0 — Direct

Choose G0 only when the change is:

- clear and bounded;
- conventional in the current environment;
- readily reversible or low consequence;
- easy to verify through an existing feedback loop;
- free of material unresolved human decisions; and
- likely to fit one implementation run.

The recipe contains no planning skill. Produce a direct implementation launch packet containing the original intent, relevant constraints, verification expectation, and escalation triggers.

### 9.6 Assurance floor

Risk does not automatically imply G3. Instead:

- security, data migration, authentication, public API compatibility, irreversible operations, or hard-to-observe failures normally rule out G0;
- use G1 plus `High-assurance` when the route is known and no human decision is missing;
- use G2 plus `High-assurance` when trade-offs or approvals are human-owned; and
- use G3 only when persistence/decomposition is independently required.

## 10. Collaboration modifiers

| Modifier | Behavioural contract |
| --- | --- |
| Educational | Explain unfamiliar concepts and trade-offs before requesting a decision. Do not turn every implementation detail into a lesson. |
| Delegated judgement | The planner may choose conventional defaults in named areas, but must record assumptions and consequences. |
| Human-decision | Present options and a recommendation, then wait for the human at named decision boundaries. |
| High-assurance | Require stronger evidence, failure analysis, verification seams, compatibility/rollback treatment, or specialist review in the eventual plan. |
| Discovery-first | Resolve a factual or empirical unknown through repository research, external primary-source research, or a prototype before committing to the affected decision. |
| Checkpointed | Return to the human at explicit gates rather than only at the end. |
| Exception-only | Proceed autonomously within stated boundaries and interrupt only when an escalation trigger is met. |

Modifiers can coexist when they are not contradictory. If a recipe contains both Delegated judgement and Human-decision, name the decision domains belonging to each.

Do not automatically bind Educational to the multi-session `teach` skill. Use `teach` only if learning itself becomes a separate durable mission rather than an interaction style within planning.

## 11. MVP planning registry

Implement `references/planning-registry.md` as a human-readable registry with one structured section per skill. It is the authoritative binding source for Gauge, not a copy of every upstream instruction.

Every entry must include:

- canonical name;
- ecosystem and upstream URL;
- capability tags;
- user-invoked or model-invoked status;
- prerequisites and dependencies;
- suitable scenarios;
- unsuitable scenarios;
- accepted context;
- expected output;
- continuation or downstream skills;
- invocation examples for supported harnesses when known; and
- optional human annotations: `preferred`, `allowed`, `discouraged`, or `prohibited`.

The bundled MVP registry should contain these entries:

### 11.1 `setup-matt-pocock-skills`

Role: repository setup prerequisite for tracker-backed engineering flows. Recommend running it once per repository before `to-spec`, `to-tickets`, or Wayfinder when tracker/domain-doc configuration is absent.

Do not treat setup as part of substantive planning.

### 11.2 `handoff`

Role: compact the current conversation into a document for a fresh agent. Use for G1 or at a phase/session boundary. It references existing artifacts instead of duplicating them and is not a substitute for unresolved planning.

Source: [handoff/SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md)

### 11.3 `grill-me` and `grilling`

Role: stateless interactive elicitation when no repository-backed paper trail is needed. `grill-me` is the user-facing entry point; `grilling` is its required interview primitive.

Do not recommend installing `grill-me` alone.

Sources: [grill-me documentation](https://github.com/mattpocock/skills/blob/main/docs/productivity/grill-me.md) and [grilling/SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md)

### 11.4 `grill-with-docs`, `grilling`, and `domain-modeling`

Role: interactive planning in a repository when shared terminology and hard decisions should be written into `CONTEXT.md` and ADRs. It is a single-session planning tool.

All three dependencies must be present. Recommend checking that the runtime actually loaded `grilling` and `domain-modeling` if behaviour degrades into an undifferentiated question dump.

Source: [grill-with-docs/SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md)

### 11.5 `to-spec`

Role: synthesize already-made decisions and current context into a durable spec; it does not perform the main interview. Use when decisions must survive a multi-session build or after a cleared Wayfinder map.

Prerequisite: repository tracker configuration through `setup-matt-pocock-skills`.

Source: [to-spec/SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-spec/SKILL.md)

### 11.6 `to-tickets`

Role: split a settled plan/spec/conversation into agent-sized tracer-bullet tickets with blocking edges. Use after `to-spec` for multi-session implementation, not as a substitute for unresolved decisions.

Prerequisite: repository tracker configuration through `setup-matt-pocock-skills`.

Source: [to-tickets/SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md)

### 11.7 `wayfinder`

Role: navigate a destination whose route is too foggy and extensive for one agent session. It maintains a map of decision tickets, resolves them over multiple sessions, and hands off when the route is clear.

Use only for G3-B. Do not use for a well-scoped single-session feature or for a large effort whose decisions are already settled.

Prerequisites: tracker setup; `grilling` and `domain-modeling` for interactive decision tickets; optional `research` and `prototype` capabilities as required by ticket type.

Source: [wayfinder/SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md)

### 11.8 `research`

Role: Discovery-first modifier for a decision blocked on trustworthy external facts. It should produce cited findings, not make the blocked human decision.

### 11.9 `prototype`

Role: Discovery-first modifier when a runnable or visible artifact is needed to answer how something should behave or look. The prototype answers a design question; it is not production implementation.

### 11.10 Explicit exclusions

- Do not recommend `ask-matt`; it is another router and adds indirection beneath Gauge.
- Do not treat `implement`, `tdd`, or `code-review` as planning ingredients. They may appear only as the downstream implementation boundary.
- Do not recommend `teach` merely because Educational is present.
- Do not add third-party ecosystems in the MVP.

### 11.11 Installation guidance

The registry must record the currently documented installation routes:

- Claude Code managed plugin: `claude plugins install mattpocock-skills`, or `/plugin install mattpocock-skills` inside a session.
- Codex and other compatible agents: `npx skills@latest add mattpocock/skills`.
- Repository preparation: run `/setup-matt-pocock-skills` once per repository when required.

When selective installation is offered, expand dependencies explicitly. Never advise installing both the managed plugin and editable `skills.sh` copy into the same environment because that creates duplicates.

Source: [official installation instructions](https://github.com/mattpocock/skills#installation-30-second-setup)

### 11.12 Availability states

Use only these availability labels:

- `installed`: the current environment explicitly exposes the skill;
- `not detected`: the environment exposes an inventory and the skill is absent;
- `unknown`: the runtime does not provide enough evidence.

Do not convert `unknown` into `not installed`. When a required skill is not detected or unknown, include exact installation and dependency instructions in the recipe.

The MVP does not auto-refresh the registry, crawl marketplaces, or update installed skills. Human edits to `planning-registry.md` are authoritative.

### 11.13 No matching skill

`No registry match` is a resolution outcome, not an availability state. Use it when none of the curated skills provides the capability the selected topology requires. The result must remain honest and actionable about the gap, but must not recommend a theoretical or invented skill merely to make the recipe appear complete.

## 12. Executable recipe contract

Every Gauge result must use this semantic structure. Wording can vary; fields cannot be silently omitted when relevant. Since ADR 0017, every execution boundary also carries `Capability`, `Model`, `Reasoning effort`, and `Runtime availability`: each step, and in G1–G3 the Implementation handoff. `references/recipe-contract.md` is authoritative for those fields.

```markdown
# Gauge result

## Verdict
- Topology: <G0 Direct | G1 Handoff | G2 Interactive | G3 Navigated>
- Variant: <optional>
- Modifiers: <none or list>
- Confidence: <High | Medium | Low>

## Why this fits
<Concise evidence from work topology, knowledge location, continuity, risk, and human context.>

## Human collaboration contract
- Human decides: <named decision domains>
- Agent may decide: <named delegated domains>
- Explain before deciding: <areas>
- Checkpoints: <gates>

## Resolved planning recipe

### Step 1 — <purpose>
- Skill: <canonical skill or "No planning skill">
- Availability: <installed | not detected | unknown | n/a>
- Invocation: <exact user action>
- Inputs: <intent and artifacts>
- Expected output: <artifact>
- Exit condition: <observable completion>
- Next handoff: <recipient and input>

#### Launch packet
```text
<copy-paste-ready prompt>
```

<Repeat per step.>

## Installation required
<Only when applicable; include dependencies and official source.>

## Implementation handoff
<What the implementation agent receives and how it should be launched.>

## Escalate or re-Gauge if
- <observable trigger>

## Assumptions and unknowns
- <only consequential items>
```

### 12.1 Launch-packet requirements

Each launch packet must include:

1. the target skill or agent role;
2. the original intent, quoted or faithfully preserved;
3. relevant environment context and artifact references;
4. confirmed constraints and exclusions;
5. the human collaboration contract;
6. the required output and its recipient;
7. the completion condition;
8. a firm `plan, do not implement` boundary for planning steps; and
9. escalation conditions.

The packet must not restate or compete with the selected skill's internal method. The skill owns **how** it performs its planning discipline; Gauge supplies **what**, **context**, **human interaction**, **output**, and **handoff**.

### 12.2 Single-step recipes

For a one-skill recipe, the recipe's launch packet must be directly pasteable after invoking that skill.

### 12.3 Multi-step recipes

The entire recipe may be given to an orchestration agent. Each individual skill receives only its own launch packet plus referenced upstream artifacts.

Do not dump the whole recipe into the first skill and assume it can invoke later user-only skills. Matt Pocock's current collection distinguishes user-invoked and model-invoked skills.

### 12.4 G0 recipe

G0 must still be executable. Use:

- `Topology: G0 Direct`;
- `Skill: No planning skill`;
- one implementation launch packet;
- verification expectations; and
- escalation triggers.

Do not insert a ceremonial spec or handoff step.

## 13. Confidence and ambiguity

Use qualitative confidence:

- **High:** the intent, continuity, knowledge location, and collaboration posture are sufficiently clear; missing details are unlikely to change the topology.
- **Medium:** some assumptions remain, but the selected topology is likely stable.
- **Low:** an unanswered question could reasonably change the topology or decision ownership.

If confidence would be Low and one small routing question can resolve it, ask before emitting the final recipe. If the user cannot or does not want to answer, emit a primary recipe with a conditional fork and make the uncertainty explicit.

Confidence describes the routing decision, not confidence that the future implementation will succeed.

## 14. Side effects and authorization

By default Gauge is read-only except for its response.

It may inspect accessible repository files, supplied artifacts, skill metadata, and explicit user/project context. It must not:

- create or modify planning artifacts;
- create tracker issues;
- install skills;
- modify the registry;
- invoke the selected planning skill; or
- start implementation.

Those actions require a later explicit user request and belong to the appropriate agent or skill.

## 15. Behavioural examples

These examples validate routing principles; do not copy their wording into every answer.

### 15.1 Bounded conventional change

Intent: Rename a local UI label with existing tests and no compatibility effect.

Expected: G0 Direct, normally Exception-only. No planning skill.

### 15.2 Small but consequential change

Intent: Change token-expiry handling in an authentication boundary. Route is known; no product choice is missing.

Expected: G1 Handoff plus High-assurance, not G0 and not automatically G3.

### 15.3 Clear feature, one implementation run

Intent: Add a bounded feature using an established repository pattern. Relevant decisions are already supplied.

Expected: G1 Handoff using `handoff`, unless the existing conversation itself is already a sufficient direct launch packet.

### 15.4 Human-held product decisions

Intent: Same bounded feature, but permissions, failure behaviour, and user-visible defaults are undecided and owned by the human.

Expected: G2 Interactive. Use `grill-with-docs` in a repository or `grill-me` outside one, then hand off.

### 15.5 Human wants to learn but delegates standards

Intent: A conventional change where the human cannot evaluate one technical area and wants enough explanation to understand it, while delegating standard implementation choices.

Expected: Base topology determined by the work; add Educational and Delegated judgement. Do not automatically promote to G2 unless an actual human decision is required.

### 15.6 Large but decided build

Intent: Architecture and behaviour are settled, but implementation requires several fresh agent sessions.

Expected: G3-A Navigated using `to-spec -> to-tickets`; no Wayfinder.

### 15.7 Large and foggy destination

Intent: Destination can be named, but interdependent technical/product decisions and investigations span sessions.

Expected: G3-B Navigated using `wayfinder -> to-spec -> to-tickets`.

### 15.8 Empirical unknown

Intent: A design choice depends on undocumented third-party behaviour or on seeing several UI variants.

Expected: Add Discovery-first using `research` or `prototype`, then continue or re-Gauge. Do not ask the human to invent the fact.

### 15.9 No skills detected

Expected: Keep the chosen topology, label availability accurately, list the exact Matt Pocock skills and dependencies to install, and provide the seed prompt. Do not hallucinate that the recipe is immediately runnable.

### 15.10 Same destination, different humans

Expert reviewer: May receive Exception-only or sparse checkpoints because they can catch edge cases.

Less experienced human seeking understanding: May receive Educational, stronger evidence, or Human-decision gates in areas they wish to own.

The topology changes only if knowledge location, continuity, or decision ownership changes—not merely because the people have different experience labels.

## 16. Acceptance criteria

The generated skill is acceptable only if all of the following hold:

1. It produces a planning recipe, not a substantive implementation plan.
2. Every non-G0 recipe names exact skills, dependencies, invocation order, expected outputs, and handoffs when the registry has a match; otherwise it explicitly reports `No registry match` without force-fitting another skill.
3. Every recipe contains copy-paste-ready launch packets.
4. G0 explicitly recommends skipping planning and contains a direct implementation packet.
5. It never emits a numerical complexity score.
6. It does not treat `expert` and `novice` as permanent identities.
7. It distinguishes explicit human facts from consequential inference.
8. It asks only routing-critical questions and does not perform the selected planning interview.
9. It distinguishes large-but-decided work from large-and-foggy work.
10. It recommends Wayfinder only for persistent, foggy navigation.
11. It does not recommend `ask-matt` beneath Gauge.
12. It does not claim a skill is installed without evidence.
13. It expands the dependencies of `grill-me` and `grill-with-docs`.
14. It gives official installation instructions when a selected skill is absent or unknown.
15. It does not invoke, install, write tracker issues, plan, or implement without a later explicit request.
16. Human edits to the bundled registry remain authoritative.
17. Its frontmatter description triggers on Gauge/planning-routing requests but not on ordinary direct implementation requests.
18. `SKILL.md` remains concise and routes detailed material into the five references.
19. Every execution boundary recommends exactly one model profile from `references/model-registry.md`, resolved by capability plus `High-assurance` when attached and never by the selected skill, or reports `No model registry match: <binding key>`. A High-assurance boundary never falls back to its base binding.
20. A profile is a canonical pinned model ID with one reasoning effort that model supports. No ordered fallback, alias, substituted model, or lowered effort appears.
21. Runtime availability reads `unavailable` with named local evidence, or `unknown`. `available` is never emitted, and no network or provider-API call is made.
22. Skill and model resolution are independent: a skill gap never removes a model profile, and a model registry gap never removes a skill binding.
23. Model recommendations are advisory: the result never claims a model or reasoning effort was applied or enforced, and reasoning effort is never presented as an estimate.
24. Human edits to the model registry remain authoritative.

## 17. Evaluation plan

Populate `evaluation-scenarios.md` from Section 15 and add at least these adversarial checks:

- A 10-minute database deletion is not treated as G0 merely because it is small.
- A large mechanical rename with known expand-contract mechanics is not sent to Wayfinder solely because many files change.
- A confident novice is not assumed able to evaluate security-sensitive judgement.
- A cautious expert is not forced into more interaction than requested when clear escalation boundaries suffice.
- A user who says `choose conventional defaults for me` receives explicit Delegated judgement rather than fake human approval gates.
- A user who says `teach me before I decide` receives Educational plus Human-decision in the named area.
- Missing repository access reduces confidence but does not trigger invented repository facts.
- A user who has already mandated Wayfinder is not rerouted away from it; Gauge may note the trade-off but must respect the explicit choice.
- An already-selected planning method does not trigger Gauge implicitly.
- Recipe text cannot be mistaken for permission to implement.
- A High-assurance recipe selects each capability's explicit `High-assurance` model binding, and reports `No model registry match: <capability> + High-assurance` where none exists.
- A runtime whose local settings cap reasoning effort below a bound profile keeps the exact recommendation and reports `unavailable` with that evidence named.
- A skill registry gap, such as a ruled-out method, still carries its capability's model profile.
- G0 and non-G0 implementation recommendations are both exercised.

Test observable decisions and side effects, not exact headings or prose. Validate the completed skill structurally using the target skill system's validator and manually inspect every scenario result.

## 18. Implementation instructions

The implementation agent should:

1. Create the `gauge` directory using the target skill initializer if available.
2. Implement only the files listed in Section 7.
3. Keep `SKILL.md` short and use progressive disclosure.
4. Populate the registry using the verified upstream sources in Section 11.
5. Treat the routing model in Sections 6, 8, and 9 as authoritative.
6. Include no auto-installation or arbitrary skill-discovery script.
7. Generate `agents/openai.yaml` using the platform helper when available.
8. Run structural validation.
9. Exercise the evaluation scenarios without modifying a real repository or tracker.
10. Report any contradiction in this specification rather than silently choosing a materially different product behaviour.

## 19. Deferred extensions

Do not implement these in the MVP:

- automatic discovery of arbitrary installed skills;
- multiple provider registries, meaning additional skill-ecosystem registries beyond the one in Section 11. The separate Anthropic model registry of ADR 0017 is not one of these; a second model provider remains deferred;
- marketplace search and quality ranking;
- generated native fallback planning protocols;
- automatic skill installation;
- automatic execution of recipes;
- persistent cross-project human proficiency models;
- telemetry or automatic learning from recipe outcomes;
- numerical effort, cost, or time estimation (a model's reasoning effort is a model control, not such an estimate); and
- a UI for editing registry entries.

The MVP file formats should remain simple enough that these can be added later without changing Gauge's core contracts.

## 20. Source notes

The initial registry and routing distinctions were verified against the upstream repository on 2026-09-04:

- [Repository and installation](https://github.com/mattpocock/skills)
- [Handoff](https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md)
- [Grill Me](https://github.com/mattpocock/skills/blob/main/docs/productivity/grill-me.md)
- [Grilling primitive](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md)
- [Grill With Docs](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md)
- [To Spec](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-spec/SKILL.md)
- [To Tickets](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md)
- [Wayfinder](https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md)

Because this upstream collection evolves, the implementation agent should preserve the date and source links in `planning-registry.md`. Future registry maintenance may update skill metadata without changing Gauge's generic routing vocabulary.
