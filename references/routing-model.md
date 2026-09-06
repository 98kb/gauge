# Routing model

How Gauge turns an intent, an environment, and a human into a topology, a set of modifiers, and a recipe template. The registry binds the template to skills; this file never names one.

## Human model

Assess only the eight properties that can change the recipe, and for each one record where the evidence came from.

| Property | The question it answers |
| --- | --- |
| Destination knowledge | Can the human recognize the correct outcome when they see it? |
| Route knowledge | Do they understand the implementation trade-offs this work involves? |
| Terrain familiarity | Do they know this repository, organization, or operational environment? |
| Evaluation ability | Can they detect a plausible error or an unsafe assumption in the result? |
| Decision ownership | Which choices do they want to make personally? |
| Delegation posture | Which choices may the agent make with conventional defaults? |
| Learning goal | Is understanding part of the desired outcome? |
| Oversight availability | How much review attention can they give? |

**Evidence order**, highest first. A lower tier never overrides a higher one:

1. explicit statements in the current request or conversation;
2. explicit user, project, or repository profile documents supplied to the agent;
3. directly observed work, decisions, or artifacts relevant to this task;
4. clearly labelled inference.

**Limits.** The evidence comes from the conversation, the supplied documents, and the task's own artifacts, and from nowhere else: no external search about the person. The model covers task-relevant knowledge and preferences only: no sensitive traits, personality, intelligence, or broad competence, and no permanent `expert` or `novice` label. Footing is read from what the human said and did; a question exists to route, never to make them prove expertise.

**Expose only consequential assumptions**, phrased narrowly about this task and separated from what the human explicitly said. The shape is:

> I am assuming you can review the TypeScript design but want security implications explained before you approve them.

A label such as "you are a novice developer" is the shape to avoid: it is broad, permanent, and about the person rather than the task.

## Knowledge location

Classify each consequential unknown by where its answer can come from. The location, not the size of the unknown, decides the move.

| Location | Routing implication |
| --- | --- |
| Current human | Add an Interactive step or a Human-decision modifier. |
| Repository or local documentation | Research it during planning; do not ask the human. |
| Established external source | Add a Discovery-first research step. |
| Planning agent's conventional judgement | Delegate explicitly and require assumptions to be recorded. |
| Another stakeholder | State that stakeholder input is required; the current agent does not impersonate them. |
| Nobody yet knows | Add research or prototype work before the affected decision is locked. |

## Topology selection

Work through these in order. The first section whose conditions hold names the dominant topology; the sections below it may still contribute a step inside the recipe.

### Destination check

A meaningful destination must be nameable before anything else is routed. When it is not, the recipe is Interactive with clarifying the destination as its purpose, plus `Discovery-first` when facts or experiments are needed before the destination can be settled. Breadth alone never makes an undefined idea G3.

### G3 Navigated

Choose G3 when decisions, planning state, or implementation decomposition must survive multiple fresh agent sessions. Persistence is the test; size and risk are not.

Then choose the variant:

- **G3-A, route already decided.** Substantive decisions are settled and the build is too large for one implementation session. Template: `durable specification -> ticket decomposition -> implementation sessions`. No navigated decision map.
- **G3-B, route still foggy.** The destination can be named, but the route holds interdependent decisions or investigations that cannot fit one planning session. Template: `navigated decision map -> durable specification -> ticket decomposition -> implementation sessions`. The map is justified by persistence *and* fog together; size alone justifies neither the map nor G3.

When a G3 recipe needs human-held knowledge elicited first, the Interactive step sits inside the G3 recipe; the dominant topology stays G3.

### G2 Interactive

Choose G2 when one or more material decisions depend on:

- tacit knowledge held by the human;
- preferences or trade-offs the human should own;
- ambiguous domain language;
- a learning goal that requires understanding before approval; or
- a decision the human is not yet ready to delegate.

The planning normally settles in one interactive planning session. Templates:

- no repository, or a non-code intent: `interactive elicitation -> implementation`;
- a repository-backed software change: `interactive elicitation with domain docs -> implementation`;
- insert `context handoff` before `implementation` when a fresh implementation session needs the settled context;
- when the implementation spans sessions, the dominant topology is G3 and this step sits inside its recipe.

### G1 Handoff

Choose G1 when all of these hold:

- the destination and material decisions are sufficiently settled;
- the agent can obtain the remaining facts from the environment;
- no substantive human interview is required;
- the work benefits from a stable context package; and
- implementation can normally proceed as one coherent run.

Template: `context handoff -> implementation`, tailored to the implementation session. A durable specification earns its cost when decisions must survive a multi-session build; adding one to a G1 recipe for formality is the ceremony this model exists to prevent.

### G0 Direct

Choose G0 only when the change is all of:

- clear and bounded;
- conventional in the current environment;
- readily reversible or low consequence;
- easy to verify through an existing feedback loop;
- free of material unresolved human decisions; and
- likely to fit one implementation run.

Template: `implementation launch packet`, with no planning skill. The packet carries the original intent, relevant constraints, the verification expectation, and escalation triggers.

### Assurance floor

Risk raises assurance, not persistence:

- security, data migration, authentication, public API compatibility, irreversible operations, or hard-to-observe failures normally rule out G0, whatever the diff size;
- G1 plus `High-assurance` when the route is known and no human decision is missing;
- G2 plus `High-assurance` when trade-offs or approvals are human-owned;
- G3 only when persistence or decomposition is independently required.

### Discovery-first placement

When a decision is blocked on an empirical or external fact (undocumented third-party behaviour, a choice that needs several variants seen), the recipe gains a `Discovery-first` step of `external research` or `design prototype` before the affected decision, and the result either feeds the next step or triggers a re-Gauge. The human is never asked to invent the fact.

### A method the human has already mandated

A planning method the human has explicitly required is respected. Gauge may note the trade-off in **Why this fits** and still binds the recipe to the mandated method. A method the human has ruled out is never bound.

## Modifiers

Attach a modifier only when it changes the behaviour of an agent executing the recipe.

| Modifier | Behavioural contract |
| --- | --- |
| Educational | Explain unfamiliar concepts and trade-offs before requesting a decision, in the named areas. Implementation detail outside those areas is not turned into a lesson. |
| Delegated judgement | The planner may choose conventional defaults in named areas, and records each assumption and its consequences. |
| Human-decision | Present options and a recommendation, then wait for the human at named decision boundaries. |
| High-assurance | The eventual plan carries stronger evidence, failure analysis, verification seams, compatibility and rollback treatment, or specialist review. |
| Discovery-first | Resolve a factual or empirical unknown through repository research, external primary-source research, or a prototype before committing to the affected decision. |
| Checkpointed | Return to the human at explicit gates rather than only at the end. |
| Exception-only | Proceed autonomously within stated boundaries and interrupt only when an escalation trigger is met. |

Modifiers coexist when they do not contradict. A recipe carrying both Delegated judgement and Human-decision names the decision domains that belong to each, so no domain is claimed by both.

Educational is an interaction style inside planning, delivered by the planning skill's launch packet. A separate multi-session teaching skill is bound only when learning has become its own durable mission rather than a style of this planning.

A user who says "choose conventional defaults for me" receives explicit Delegated judgement in the named areas, with assumptions recorded, and no approval gates pretending otherwise. A user who says "teach me before I decide" receives Educational plus Human-decision in the named area.

## Capability vocabulary

The templates above are written in provider-neutral capability names so a future registry can bind them without touching this file. The registry maps each name to a skill and its dependencies. `implementation` and `implementation sessions` in a template name the downstream boundary, not a capability; the recipe describes them under **Implementation handoff**.

| Capability | What the step must do |
| --- | --- |
| `tracker setup` | Prerequisite: configure the repository's tracker and domain-doc conventions once, before any capability that writes to a tracker. |
| `context handoff` | Compact the settled context into a document a fresh agent can continue from, referencing existing artifacts rather than duplicating them. |
| `interactive elicitation` | Interview the human in rounds until the design tree has no silently assumed branch; stateless, no repository needed. |
| `interactive elicitation with domain docs` | The same interview, aligned against a repository, recording terminology and hard decisions into the project's glossary and decision records. |
| `durable specification` | Synthesize already-made decisions and current context into a spec that survives a multi-session build; no interview. |
| `ticket decomposition` | Split a settled spec into agent-sized tracer-bullet tickets with blocking edges. |
| `navigated decision map` | Chart a destination whose route is too foggy for one session as a persistent map of decision tickets, resolved across sessions. |
| `external research` | Resolve a fact from primary sources and report cited findings, without making the blocked decision. |
| `design prototype` | Produce a throwaway runnable or visible artifact that answers a behaviour or appearance question. |
| `implementation launch packet` | No planning skill. A direct packet for the implementation agent. |
