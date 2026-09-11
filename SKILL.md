---
name: gauge
description: Assess an intent before planning, choose a Direct, Handoff, Interactive, or Navigated workflow, and produce an executable planning recipe using the configured skill registry. Use when the user asks to gauge an effort, decide how much planning it needs, choose a planning workflow, or generate a seed prompt for planning. Do not use merely because the user directly asks to implement or has already chosen a planning method.
disable-model-invocation: true
---

# Gauge

Gauge runs before planning. Given an intent, the environment it lands in, the human engaging with it, and a curated registry of planning skills, it answers one question:

> What exact process should produce the plan for this intent, or should a separate planning step be skipped?

The answer is a **planning recipe**: a base **topology**, the **modifiers** attached to it, the exact skills to start in order, one copy-paste-ready **launch packet** per step, the human's decision rights, and the triggers that send the work back here. The human can read it and override it; whoever starts each named skill, the human or an orchestrating agent, pastes that skill's packet in.

## Boundary

Gauge emits the recipe and stops. The substantive plan, the decomposition into tasks, and the implementation belong to the skills the recipe names. Gauge is read-only apart from its response: it may inspect repository files, supplied artifacts, skill metadata, and explicit user or project context. It creates no planning artifact, opens no tracker issue, installs nothing, edits no registry, and starts no planning or implementation skill; each of those needs a later, explicit request, and so does saving the recipe as a file. Gauge routes among planning skills only; it is not a router over every engineering skill.

## Topologies

The code is a compact label, not a rank. G3 is not harder or riskier than G2, and no numerical score, T-shirt size, story-point, time, or cost estimate is ever computed or shown.

| Code | Name | Contract |
| --- | --- | --- |
| G0 | Direct | Skip a separate planning phase. Hand the intent and explicit guardrails straight to an implementation agent. |
| G1 | Handoff | Produce a bounded context/specification handoff without a substantive human interview, normally for one coherent implementation run. |
| G2 | Interactive | Elicit human-held knowledge or judgement before creating the implementation handoff. |
| G3 | Navigated | Preserve decisions and decomposition across multiple planning or implementation sessions. A navigated decision map only while the route is foggy; a durable specification and tickets when the route is decided. |

Work topology and collaboration posture are separate axes. Human expertise moves the modifiers, decision ownership, explanation depth, checkpoint frequency, evidence requirements, and escalation rules. It moves the topology only when it changes where necessary knowledge resides, whether an important decision needs interaction, or whether the human can responsibly delegate it.

## Workflow

Four references carry the detail, each read at the step that needs it:

- [references/routing-model.md](references/routing-model.md): read before step 3. Owns the human-model rules, the knowledge-location table, the topology selection criteria, the assurance floor, and the modifier contracts.
- [references/planning-registry.md](references/planning-registry.md): read at step 8. The authoritative, human-edited binding source: skill metadata, dependencies, availability rules, installation guidance, recipe bindings, and the `No registry match` outcome.
- [references/model-registry.md](references/model-registry.md): read at step 8. The separate, human-edited model registry: Anthropic model profiles, their capability bindings, the `No model registry match` outcome, and the runtime-availability evidence rules.
- [references/recipe-contract.md](references/recipe-contract.md): read at step 9. The output schema, launch-packet template, and confidence grades.

[references/evaluation-scenarios.md](references/evaluation-scenarios.md) is for testing this skill, not for running it.

1. **Preserve and frame the intent.** Record the original wording verbatim, the destination or success state, explicit constraints and exclusions, whether delivery, learning, or both are wanted, and any planning method the human has already required or ruled out. The intent keeps the size the human gave it; a request is never widened into a larger initiative. Done when each of the five is recorded or marked absent.
2. **Reconnoitre the task, bounded.** Inspect the repository, project docs, tracker context, or supplied artifacts only far enough to route: affected subsystems and coupling; prior art; reversibility and rollback; security, data, compatibility, or production consequences; verification seams; whether the route is already known; whether the work fits one coherent implementation run; whether decisions must survive across sessions. Stop short of an architecture survey, a design answer, a drafted ticket, or a line of implementation. When the environment is unreachable, record the resulting assumption instead of a guess about the repository. Done when each item is located, marked absent, or recorded as an assumption because the environment was unreachable.
3. **Build a task-specific human model.** Assess only the properties the routing model names, the ones that can change the recipe, in the evidence order and within the limits it fixes. Done when each property has a reading with its evidence tier, or is marked unknown.
4. **Locate unresolved knowledge.** Classify each consequential unknown by where its answer lives, using the routing model's table. Done when every consequential unknown has a location and the routing move it implies.
5. **Ask only routing-critical questions.** Ask when an answer could change the topology, decision ownership, the need for Educational, whether delegation is safe, or whether the workflow must persist across sessions. One concise batch is usually enough. The full interview belongs to the planning skill the recipe will name; when the context already suffices, ask nothing. Done when every such unknown has an answer or a labelled assumption.
6. **Select the dominant topology** with the routing model. Done when one topology, with its variant for G3, is named together with the condition that selected it.
7. **Attach modifiers** that change agent behaviour for this recipe. A modifier that changes nothing is left off. Done when each attached modifier names the behaviour it changes and, where it is scoped, the domain it covers.
8. **Resolve the recipe.** From the planning registry choose the smallest sufficient skill sequence, label each skill's availability from evidence in the current environment, expand dependencies, and write one launch packet per step. Gauge owns routing, so no routing skill appears as a step. Separately, from the model registry, resolve one advisory model profile for every execution boundary. The boundaries are tracker setup, each planning step, the G0 implementation step, and the non-G0 Implementation handoff. Resolve by capability, plus `High-assurance` when attached, never by the chosen skill. Then label runtime availability from local, read-only evidence. Done when every step carries a bound skill, `No planning skill` for G0, or `No registry match`, plus an availability label and a packet. Every execution boundary must also carry a capability, a model profile or `No model registry match`, and a runtime-availability label; the recipe is not emitted until they all do.
9. **Emit the recipe and stop.** Follow the recipe contract, including its confidence grades. Done when the result is emitted and no skill has been started.

## Stopping condition

Gauge is finished when the reader knows: whether a distinct planning phase is needed; which skills to start, in what order, with what context and prompt; which model and reasoning effort are recommended for each session, as advice; what role the human plays; what artifact each step produces; how that artifact reaches implementation; and which findings escalate or re-Gauge. A reader who would still have to invent a prompt, or decide how planning itself is conducted, has an incomplete recipe.
