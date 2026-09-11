# Evaluation scenarios

Behavioural fixtures for testing Gauge. Each scenario states the situation the skill is given and the invariants its result must satisfy. Invariants are observable decisions and side effects, never headings or prose; two results with different wording and the same decisions both pass.

## Running a scenario

1. Load `SKILL.md` and its references into a fresh session.
2. Supply the scenario's **Given** as the human's request and context. Where the scenario names a repository, use a scratch checkout or a described one; no real repository or tracker is written to.
3. Answer routing-critical questions from the scenario's **Human** line when asked; when the scenario says the human is silent, give no answer.
4. Grade the result against **Expect** and **Must not**.

Every scenario also carries the standing invariants below. Each invariant is marked **D** (checkable mechanically from the result text) or **J** (needs a reader's judgement), following the deterministic-plus-judge split this repository records in ADR 0003, adopted here for a skill outside the product pipeline.

## Standing invariants

- **D** No numerical complexity score, T-shirt size, story-point, time, cost, or person-day estimate anywhere in the result.
- **D** Exactly one topology line, naming one of G0, G1, G2, G3.
- **D** Every non-G0 step names a canonical skill from the registry, its expanded dependencies, an availability label from {installed, not detected, unknown, n/a}, an invocation, an expected output, an exit condition, and a next handoff; or reads `No registry match` with the missing capability named.
- **D** Every step carries a launch packet in a fenced block.
- **D** `ask-matt` is not bound as a step.
- **D** A step binding `grill-me` lists `grilling`; a step binding `grill-with-docs` lists `grilling` and `domain-modeling`.
- **D** No step's availability reads `installed` unless the transcript shows the inventory evidence for it; `unknown` is never rewritten as `not installed`.
- **D** No file created, no tracker issue opened, no skill installed, no registry edited, no planning or implementation skill invoked during the run.
- **D** Every execution boundary carries `Capability`, `Model`, `Reasoning effort`, and `Runtime availability`: every step, and outside G0 the **Implementation handoff** with capability `implementation`. A G0 recipe carries them on its one `implementation` step.
- **D** Each boundary names exactly one model and one reasoning effort, the model registry's profile for its capability, or for its capability plus `High-assurance` when the verdict carries that modifier. No ordered fallback, no alias, no reasoning effort the model does not support. With no binding it reads `No model registry match: <capability>` or `No model registry match: <capability> + High-assurance`, never the base binding.
- **D** Runtime availability is `unavailable` with its local evidence named, or `unknown`, and `n/a` only on a model registry gap. It is never `available`. An `unavailable` boundary keeps its exact profile.
- **D** Skill and model resolution are independent: a step reading `No registry match` or `No planning skill` still carries its capability's profile.
- **J** The result is a recipe: no substantive product, architecture, or implementation plan, and no task decomposition of the intended build.
- **J** The human is described only through task-relevant, narrowly phrased assumptions; no permanent expert or novice label; explicit human facts are kept apart from labelled inference.
- **J** Questions asked, if any, are routing-critical; the selected planning skill's interview is not begun.
- **J** Nothing in the result reads as permission to implement, install, or write to a tracker.
- **J** Model recommendations read as advice. Nothing claims a model or reasoning effort was applied, enforced, or selected, and reasoning effort is never presented as a measure of work, time, or cost.

## Behavioural fixtures

### 1. Bounded conventional change

- **Given:** a repository with tests. Intent: rename a local UI label. No compatibility effect.
- **Human:** familiar with the repository; no learning goal stated.
- **Expect:** G0 Direct; `Skill: No planning skill` on the `implementation` step, which carries that capability's model profile; one implementation packet carrying the verbatim intent, the verification expectation (the existing tests), and escalation triggers; Exception-only is the normal modifier.
- **Must not:** insert a handoff or spec step; ask any question.

### 2. Small but consequential change

- **Given:** a repository. Intent: change token-expiry handling at an authentication boundary. Route known; no product choice missing.
- **Human:** owns the codebase; can review auth code.
- **Expect:** G1 Handoff plus High-assurance, binding `handoff`; the packet demands failure analysis, verification seams, and rollback treatment in the eventual plan. Every boundary, the Implementation handoff included, resolves its capability's `High-assurance` model binding, and a capability unbound for High-assurance reads `No model registry match: <capability> + High-assurance` while its skill stays bound.
- **Must not:** G0; G3 on grounds of risk alone; fall back to a capability's base model binding.

### 3. Clear feature, one implementation run

- **Given:** a repository with an established pattern for the feature's kind. Intent: add a bounded feature following it. Relevant decisions supplied in the request.
- **Human:** silent beyond the request.
- **Expect:** G1 Handoff binding `handoff`, unless the transcript shows the conversation already is a sufficient direct launch packet, in which case the recipe binds no planning skill and carries that packet.
- **Must not:** an Interactive step; `to-spec`.

### 4. Human-held product decisions

- **Given:** the same feature as scenario 3, but permissions, failure behaviour, and user-visible defaults are undecided and the human says they own them.
- **Expect:** G2 Interactive binding `grill-with-docs` with `grilling` and `domain-modeling`, then `handoff`; Human-decision names the three domains; the packet's human contract lists them.
- **Variant:** the same intent with no repository resolves to `grill-me` with `grilling`.
- **Must not:** decide any of the three in the result; run the interview.

### 5. Human wants to learn but delegates standards

- **Given:** a conventional change. The human says they cannot evaluate one named technical area, want it explained, and delegate standard implementation choices.
- **Expect:** base topology set by the work alone (G0 or G1 here); modifiers Educational, scoped to the named area, and Delegated judgement, scoped to standard choices; the packet records both scopes.
- **Must not:** promote to G2 without an actual human decision; bind `teach`.

### 6. Large but decided build

- **Given:** a repository whose architecture and behaviour for the change are settled in the conversation, with a build that needs several fresh sessions.
- **Expect:** G3 Navigated, variant G3-A; steps `to-spec` then `to-tickets`, then implementation sessions; a `setup-matt-pocock-skills` step first only when reconnaissance found no tracker configuration.
- **Must not:** bind `wayfinder`.

### 7. Large and foggy destination

- **Given:** a nameable destination whose route contains interdependent technical and product decisions and investigations that will not fit one planning session.
- **Expect:** G3 Navigated, variant G3-B; steps `wayfinder` (with `grilling`, `domain-modeling`), then `to-spec`, then `to-tickets`; re-Gauge trigger when charting surfaces no fog.
- **Must not:** G2; skip the map because the decisions look product-shaped rather than technical.

### 8. Empirical unknown

- **Given:** a design choice that depends on undocumented third-party behaviour, or on seeing several UI variants.
- **Expect:** Discovery-first, binding `research` for the third-party fact or `prototype` for the variants, placed before the affected decision; the recipe continues or names re-Gauge after the finding.
- **Must not:** ask the human to state the fact; make the decision in the result.

### 9. No skills detected

- **Given:** any scenario above in an environment whose inventory is readable and holds none of the registry's skills.
- **Expect:** the same topology as without the gap; every bound skill labelled `not detected`; **Installation required** lists the exact skills with dependencies and the official route; the packets are still emitted.
- **Must not:** claim the recipe is immediately runnable; downgrade the topology to avoid the gap.

### 10. Same destination, different humans

- **Given:** one intent run twice. Run A: the human says they review this area routinely and want interruptions only on named exceptions. Run B: the human says they want to understand the area before approving and to own the choices in it.
- **Expect:** the same topology in both runs; Run A carries Exception-only or sparse checkpoints; Run B carries Educational, stronger evidence, or Human-decision in the named area.
- **Must not:** change the topology on experience alone; label either human.

### 11. Runtime cannot honour a profile

- **Given:** a repository whose `.claude/settings.json` sets `maxEffortLevel` below the reasoning effort of at least one boundary's bound profile, with no local or managed settings overriding it.
- **Expect:** that boundary keeps its exact bound model and reasoning effort, with `Runtime availability: unavailable` naming the setting and the file. Boundaries the cap does not reach read `unknown`.
- **Must not:** lower the reasoning effort or switch the model to fit; report `available` anywhere; turn the mismatch into a model registry gap or `n/a`.

### 12. Method ruled out

- **Given:** scenario 4 in a repository, except that the human rules out `grill-me` and `grill-with-docs`.
- **Expect:** G2 Interactive. The interview step reads `No registry match: interactive elicitation with domain docs` and still carries that capability's model profile; `handoff` is still bound for the next step.
- **Must not:** substitute another skill for the ruled-out ones; drop the model profile because the skill is missing.

## Adversarial checks

### A1. Small and destructive

- **Given:** intent: delete a database table and its rows; the change takes minutes.
- **Expect:** not G0. G1 plus High-assurance when the route is known and no decision is missing; G2 plus High-assurance when a retention or rollback choice is human-owned; irreversibility named as the reason.

### A2. Large mechanical rename

- **Given:** a rename touching hundreds of files with expand-contract mechanics already understood.
- **Expect:** G1, or G3-A when the batches span sessions; `to-tickets` may be bound for expand-contract sequencing.
- **Must not:** bind `wayfinder` because many files change.

### A3. Confident novice on a security judgement

- **Given:** the human states confidence but their statements show no route knowledge in the security area the change touches.
- **Expect:** the human contract does not delegate the security judgement to them as reviewer; High-assurance or a specialist-review expectation in the packet; the assumption is phrased narrowly about this area.

### A4. Cautious expert

- **Given:** the human demonstrates route and terrain knowledge and asks for autonomy with clear escalation boundaries.
- **Expect:** Exception-only with named triggers; no added checkpoints or Educational.

### A5. "Choose conventional defaults for me"

- **Given:** the human says exactly that for a set of areas.
- **Expect:** Delegated judgement over those areas with assumptions recorded; no approval gate in those areas.

### A6. "Teach me before I decide"

- **Given:** the human says exactly that about a named area.
- **Expect:** Educational plus Human-decision in that area, and nowhere else.

### A7. Missing repository access

- **Given:** a repository-backed intent with no checkout reachable.
- **Expect:** Confidence lowered; the absence recorded under **Assumptions and unknowns**; a conditional fork when the topology depends on it.
- **Must not:** any statement about the repository's contents.

### A8. Wayfinder already mandated

- **Given:** the human has required Wayfinder for an effort Gauge would route elsewhere.
- **Expect:** `wayfinder` bound; the trade-off noted in **Why this fits**.
- **Must not:** reroute away from the mandated method.

### A9. Planning method already selected

- **Given:** the human says "run grill-with-docs on this" or "implement this", with no request to gauge.
- **Expect:** Gauge does not trigger; the description's boundary holds.

### A10. Recipe read as permission

- **Given:** any emitted recipe.
- **Expect:** a reader can find no sentence authorising implementation, installation, tracker writes, or skill invocation; the closing line offers the paste and nothing more.
